import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from agents.internal.base import BaseAgent
from agents.internal.config import AgentConfig
from agents.orchestrator.base import BaseOrchestrator
from langchain_core.tools import StructuredTool

from .helpers import make_agent_response, make_orchestrator_response, make_request


def run(coroutine):
    return asyncio.run(coroutine)


def agent_config(name="dummy"):
    return AgentConfig(
        name=name,
        description="A test agent",
        system_prompt="Be precise.",
    )


class DummyAgent(BaseAgent):
    def get_tools(self):
        return []


class FakeGraph:
    def __init__(self, result):
        self.result = result
        self.calls = []

    async def ainvoke(self, state, *, context=None, config=None):
        self.calls.append((state, context, config))
        return self.result


def test_base_agent_renders_requests_and_builds_with_mcp_tools():
    model = object()
    created = {}

    def fake_create_agent(**kwargs):
        created.update(kwargs)
        return "graph"

    async def fake_mcp_tools(_):
        return ["mcp-tool"]

    with (
        patch("agents.internal.base.load_agent_yaml", return_value=agent_config()),
        patch("agents.internal.base.aload_agent_mcp_tools", fake_mcp_tools),
        patch("agents.internal.base.create_agent", fake_create_agent),
    ):
        agent = DummyAgent(model=model)
        graph = run(agent.abuild())

    assert graph == "graph"
    assert created["model"] is model
    assert created["tools"] == ["mcp-tool"]
    assert "Task objective:\nReview the pull request" in agent._render_request(
        make_request()
    )
    assert "owner=acme" in agent._render_request(make_request())


def test_base_agent_caches_graph_and_invokes_structured_output():
    response = make_agent_response()
    graph = FakeGraph({"structured_response": response.model_dump()})

    with patch("agents.internal.base.load_agent_yaml", return_value=agent_config()):
        agent = DummyAgent(model=object())
    agent._graph = graph

    result = run(
        agent.ainvoke_structured(make_request(), context={"github_token": "x"})
    )
    assert result == response
    assert graph.calls[0][1] == {"github_token": "x"}
    assert graph.calls[0][0]["messages"][0].content.startswith("Task objective:")
    assert run(agent.abuild()) is graph


def test_base_agent_reports_missing_structured_output():
    with patch("agents.internal.base.load_agent_yaml", return_value=agent_config()):
        agent = DummyAgent(model=object())
    agent._graph = FakeGraph({})

    with pytest.raises(RuntimeError, match="structured response"):
        run(agent.ainvoke_structured(make_request()))


def test_base_agent_exposes_a_structured_tool():
    with patch("agents.internal.base.load_agent_yaml", return_value=agent_config()):
        agent = DummyAgent(model=object())

    tool = agent.as_tool()
    assert isinstance(tool, StructuredTool)
    assert tool.name == "dummy"
    assert set(tool.args_schema.model_fields) == {"task_objective", "focus"}


def test_base_orchestrator_renders_and_invokes_structured_response():
    config = agent_config("orchestrator")
    orchestrator = BaseOrchestrator(object(), config, [])
    expected = make_orchestrator_response()
    graph = FakeGraph({"structured_response": expected.model_dump()})
    orchestrator._graph = graph

    result = run(
        orchestrator.ainvoke_structured(
            make_request(), github_token="secret", thread_id="thread-1"
        )
    )

    assert result == expected
    state, context, graph_config = graph.calls[0]
    assert state["messages"][0].content.startswith("Task objective:")
    assert context.github_token == "secret"
    assert graph_config == {"configurable": {"thread_id": "thread-1"}}
    assert "Focus and context" in orchestrator._render_request(make_request())


def test_base_orchestrator_reports_missing_response():
    orchestrator = BaseOrchestrator(object(), agent_config("orchestrator"), [])
    orchestrator._graph = FakeGraph({})

    with pytest.raises(RuntimeError, match="structured response"):
        run(orchestrator.ainvoke_structured(make_request(), thread_id="thread-1"))


def test_base_orchestrator_builds_specialist_and_mcp_tools():
    specialist = SimpleNamespace(abuild=AsyncMock(), as_tool=lambda: "specialist-tool")
    created = {}

    def fake_create_agent(**kwargs):
        created.update(kwargs)
        return "graph"

    async def no_mcp(_):
        return ["mcp-tool"]

    orchestrator = BaseOrchestrator(
        object(), agent_config("orchestrator"), [specialist]
    )
    with (
        patch("agents.orchestrator.base.aload_agent_mcp_tools", no_mcp),
        patch("agents.orchestrator.base.create_agent", fake_create_agent),
    ):
        assert run(orchestrator.abuild()) == "graph"

    specialist.abuild.assert_awaited_once()
    assert created["tools"] == ["specialist-tool", "mcp-tool"]
