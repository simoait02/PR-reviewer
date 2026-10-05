import asyncio
from types import SimpleNamespace

from agents.review_pipeline import ReviewPipeline

from .helpers import (
    make_orchestrator_response,
    make_patch_response,
    make_request,
    make_synthesizer_response,
)


class FakeGraph:
    def __init__(self, updates=None, result=None):
        self.updates = updates or []
        self.result = result
        self.astream_calls = []
        self.ainvoke_calls = []

    async def astream(self, state, *, context, stream_mode):
        self.astream_calls.append((state, context, stream_mode))
        for update in self.updates:
            yield update

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


class FakePatch:
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
        updates=[
            {"orchestrator": {"orchestrator_response": make_orchestrator_response()}},
            {"patch": {"patch_response": make_patch_response()}},
            {"synthesizer": synthesizer.model_dump()},
        ]
    )
    pipeline = ReviewPipeline(None, None, None)
    pipeline._graph = graph

    events = collect(
        pipeline.astream(make_request(), github_token="secret", thread_id="thread-1")
    )

    assert [event_name for event_name, _ in events] == [
        "status",
        "summary",
        "findings",
        "limitations",
    ]
    assert events[0] == ("status", {"status": "completed"})
    assert events[1] == ("summary", {"summary": synthesizer.summary})
    assert events[2][1]["severity"] == "high"
    assert events[3] == ("limitations", {"limitation": synthesizer.limitations[0]})
    assert graph.astream_calls[0][1] == {"github_token": "secret"}
    assert graph.astream_calls[0][2] == "updates"


def test_astream_ignores_updates_without_synthesizer_output():
    graph = FakeGraph(updates=[{"orchestrator": {}}, {"patch": {}}])
    pipeline = ReviewPipeline(None, None, None)
    pipeline._graph = graph

    assert collect(pipeline.astream(make_request(), thread_id="thread-1")) == []


def test_ainvoke_validates_typed_final_response():
    expected = make_synthesizer_response()
    graph = FakeGraph(result=expected.model_dump())
    pipeline = ReviewPipeline(None, None, None)
    pipeline._graph = graph

    result = asyncio.run(
        pipeline.ainvoke(make_request(), github_token="secret", thread_id="thread-1")
    )

    assert result == expected
    assert graph.ainvoke_calls[0][0]["thread_id"] == "thread-1"
    assert graph.ainvoke_calls[0][1] == {"github_token": "secret"}


def test_pipeline_nodes_forward_context_and_chain_outputs():
    orchestrator_response = make_orchestrator_response()
    patch_response = make_patch_response()
    synthesizer_response = make_synthesizer_response()
    orchestrator = FakeOrchestrator(orchestrator_response)
    patch = FakePatch(patch_response)
    synthesizer = FakeSynthesizer(synthesizer_response)
    pipeline = ReviewPipeline(orchestrator, patch, synthesizer)
    runtime = SimpleNamespace(context={"github_token": "secret"})

    async def run():
        orchestrator_update = await pipeline._run_orchestrator(
            {"request": make_request(), "thread_id": "thread-1"},
            runtime=runtime,
        )
        patch_update = await pipeline._run_patch(
            {
                "orchestrator_response": orchestrator_update["orchestrator_response"],
                "thread_id": "thread-1",
            },
            runtime=runtime,
        )
        synthesizer_update = await pipeline._run_synthesizer(
            {
                "orchestrator_response": orchestrator_update["orchestrator_response"],
                "patch_response": patch_update["patch_response"],
            }
        )
        return orchestrator_update, patch_update, synthesizer_update

    orchestrator_update, patch_update, synthesizer_update = asyncio.run(run())
    assert orchestrator_update == {"orchestrator_response": orchestrator_response}
    assert patch_update == {"patch_response": patch_response}
    assert synthesizer_update == synthesizer_response.model_dump()
    assert orchestrator.calls[0][1:] == ("secret", "thread-1")
    assert patch.calls[0][1:] == ("secret", "thread-1:patch")
    assert synthesizer.calls[0].orchestrator_response == orchestrator_response
