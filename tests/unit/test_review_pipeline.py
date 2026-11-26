import asyncio
from types import SimpleNamespace

from agents.review_pipeline import ReviewPipeline

from .helpers import (
    make_orchestrator_response,
    make_request,
    make_synthesizer_response,
)


class FakeGraph:
    def __init__(self, events=None, result=None):
        self.events = events or []
        self.result = result
        self.astream_events_calls = []
        self.ainvoke_calls = []

    async def astream_events(self, state, *, context, version):
        self.astream_events_calls.append((state, context, version))
        for event in self.events:
            yield event

    async def ainvoke(self, state, *, context):
        self.ainvoke_calls.append((state, context))
        return self.result


class FakeOrchestrator:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def ainvoke_structured(self, request, *, github_token, thread_id):
        self.calls.append((request, github_token, thread_id))
        return self.response


class FakeSynthesizer:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def ainvoke_structured(self, request):
        self.calls.append(request)
        return self.response


def collect(async_iterator):
    async def run():
        return [item async for item in async_iterator]

    return asyncio.run(run())


def test_astream_exposes_only_synthesizer_fields():
    synthesizer = make_synthesizer_response()
    graph = FakeGraph(
        events=[
            {
                "event": "on_chain_start",
                "name": "orchestrator",
                "data": {},
                "metadata": {},
            },
            {
                "event": "on_chain_end",
                "name": "orchestrator",
                "data": {
                    "output": {
                        "orchestrator_response": make_orchestrator_response().model_dump(
                            mode="json"
                        )
                    }
                },
                "metadata": {},
            },
            {
                "event": "on_tool_start",
                "name": "review_tool",
                "data": {},
                "metadata": {},
            },
            {
                "event": "on_tool_end",
                "name": "review_tool",
                "data": {},
                "metadata": {},
            },
            {
                "event": "on_parser_stream",
                "name": "synthesizer_parser",
                "data": {"chunk": {"summary": "A summary"}},
                "metadata": {"langgraph_node": "synthesizer"},
            },
            {
                "event": "on_chain_end",
                "name": "synthesizer",
                "data": {"output": synthesizer.model_dump(mode="json")},
                "metadata": {},
            },
        ]
    )
    pipeline = ReviewPipeline(None, None)
    pipeline._graph = graph

    events = collect(
        pipeline.astream(make_request(), github_token="secret", thread_id="thread-1")
    )

    response_events = [
        event
        for event in events
        if event[0] in {"status", "summary", "findings", "limitations"}
    ]
    assert {event_name for event_name, _ in events} <= {
        "status",
        "summary",
        "findings",
        "limitations",
        "stream_event",
        "token",
    }
    assert [event_name for event_name, _ in response_events] == [
        "status",
        "summary",
        "findings",
        "limitations",
    ]
    assert response_events[0] == ("status", {"status": "completed"})
    assert response_events[1] == ("summary", {"summary": synthesizer.summary})
    assert response_events[2][1]["severity"] == "high"
    assert response_events[3] == (
        "limitations",
        {"limitation": synthesizer.limitations[0]},
    )
    assert ("stream_event", {"type": "agent_started", "name": "orchestrator"}) in events
    assert ("stream_event", {"type": "tool_started", "name": "review_tool"}) in events
    assert ("token", {"token": "A summary"}) in events
    assert graph.astream_events_calls[0][1] == {"github_token": "secret"}
    assert graph.astream_events_calls[0][2] == "v2"


def test_astream_ignores_events_without_synthesizer_output():
    graph = FakeGraph(
        events=[
            {
                "event": "on_chain_end",
                "name": "orchestrator",
                "data": {"output": {"orchestrator_response": {}}},
                "metadata": {},
            }
        ]
    )
    pipeline = ReviewPipeline(None, None)
    pipeline._graph = graph

    assert collect(pipeline.astream(make_request(), thread_id="thread-1")) == []


def test_ainvoke_validates_typed_final_response():
    expected = make_synthesizer_response()
    graph = FakeGraph(result=expected.model_dump())
    pipeline = ReviewPipeline(None, None)
    pipeline._graph = graph

    result = asyncio.run(
        pipeline.ainvoke(make_request(), github_token="secret", thread_id="thread-1")
    )

    assert result == expected
    assert graph.ainvoke_calls[0][0]["thread_id"] == "thread-1"
    assert graph.ainvoke_calls[0][1] == {"github_token": "secret"}


def test_pipeline_nodes_forward_context_and_chain_outputs():
    orchestrator_response = make_orchestrator_response()
    synthesizer_response = make_synthesizer_response()
    orchestrator = FakeOrchestrator(orchestrator_response)
    synthesizer = FakeSynthesizer(synthesizer_response)
    pipeline = ReviewPipeline(orchestrator, synthesizer)

    async def run():
        orchestrator_update = await pipeline._run_orchestrator(
            {"request": make_request(), "thread_id": "thread-1"},
            runtime=SimpleNamespace(context={"github_token": "secret"}),
        )
        synthesizer_update = await pipeline._run_synthesizer(
            {
                "orchestrator_response": orchestrator_update["orchestrator_response"],
            }
        )
        return orchestrator_update, synthesizer_update

    orchestrator_update, synthesizer_update = asyncio.run(run())
    assert orchestrator_update == {"orchestrator_response": orchestrator_response}
    assert synthesizer_update == synthesizer_response.model_dump()
    assert orchestrator.calls[0][1:] == ("secret", "thread-1")
    assert synthesizer.calls[0].orchestrator_response == orchestrator_response
