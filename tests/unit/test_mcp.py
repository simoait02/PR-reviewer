import asyncio
from types import SimpleNamespace

import pytest
from agents.mcp import loader
from agents.mcp.config import AgentMCPServer, MCPServer
from langchain_mcp_adapters.interceptors import MCPToolCallRequest


def run(coroutine):
    return asyncio.run(coroutine)


def request(
    name="github_orchestrator_get_pr_info",
    *,
    args=None,
    context=None,
    headers=None,
):
    return MCPToolCallRequest(
        name=name,
        args=args or {"pull_number": 42},
        server_name="github_orchestrator",
        headers=headers,
        runtime=SimpleNamespace(context=context) if context is not None else None,
    )


def test_github_token_interceptor_adds_token_without_mutating_original_request():
    received = []

    async def handler(received_request):
        received.append(received_request)
        return "ok"

    original = request(context={"github_token": "secret"}, headers={"X-Test": "yes"})
    assert run(loader.github_token_interceptor(original, handler)) == "ok"

    assert original.headers == {"X-Test": "yes"}
    assert received[0].headers == {"X-Test": "yes", "X-GitHub-Token": "secret"}


def test_github_token_interceptor_passes_request_through_without_token():
    received = []

    async def handler(received_request):
        received.append(received_request)
        return "ok"

    original = request(context={"github_token": None})
    run(loader.github_token_interceptor(original, handler))
    assert received == [original]


def test_runtime_token_and_registry_loading(monkeypatch, tmp_path):
    assert loader._runtime_github_token(None) is None
    assert (
        loader._runtime_github_token(SimpleNamespace(context={"github_token": "x"}))
        == "x"
    )

    registry_file = tmp_path / "servers.yaml"
    registry_file.write_text(
        "servers:\n  orchestrator:\n    url: http://default:9000/mcp\n    timeout: 12\n"
    )
    monkeypatch.setattr(loader, "_REGISTRY_PATH", registry_file)
    monkeypatch.setenv("ORCHESTRATOR_MCP_URL", "http://override:9000/mcp")

    registry = loader._load_registry()
    assert registry == {
        "orchestrator": MCPServer(url="http://override:9000/mcp", timeout=12)
    }


def test_load_mcp_tools_handles_empty_unknown_and_failure(monkeypatch):
    assert run(loader.aload_agent_mcp_tools([])) == []

    monkeypatch.setattr(loader, "_load_registry", dict)
    with pytest.raises(ValueError, match="Unknown MCP server"):
        run(loader.aload_agent_mcp_tools([AgentMCPServer(name="missing")]))

    monkeypatch.setattr(
        loader,
        "_load_registry",
        lambda: {"orchestrator": MCPServer(url="http://orchestrator/mcp")},
    )

    async def unavailable(**_):
        raise RuntimeError("offline")

    monkeypatch.setattr(loader, "load_mcp_tools", unavailable)
    assert (
        run(loader.aload_agent_mcp_tools([AgentMCPServer(name="orchestrator")])) == []
    )


def test_load_mcp_tools_collects_tools(monkeypatch):
    monkeypatch.setattr(
        loader,
        "_load_registry",
        lambda: {"orchestrator": MCPServer(url="http://orchestrator/mcp")},
    )

    async def available(**_):
        return ["tool-1", "tool-2"]

    monkeypatch.setattr(loader, "load_mcp_tools", available)
    result = run(loader.aload_agent_mcp_tools([AgentMCPServer(name="orchestrator")]))
    assert result == ["tool-1", "tool-2"]
