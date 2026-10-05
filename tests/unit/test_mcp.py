import asyncio
from types import SimpleNamespace

import pytest
from agents.mcp import cache, loader
from agents.mcp.config import AgentMCPServer, MCPServer
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from mcp.types import CallToolResult, TextContent


def run(coroutine):
    return asyncio.run(coroutine)


def request(
    name="github_reviewer_get_file_content",
    *,
    args=None,
    context=None,
    headers=None,
):
    return MCPToolCallRequest(
        name=name,
        args=args or {"file_sha": "abc"},
        server_name="github_reviewer",
        headers=headers,
        runtime=SimpleNamespace(context=context) if context is not None else None,
    )


def successful_result():
    return CallToolResult(content=[TextContent(type="text", text="ok")])


def test_cache_key_removes_server_prefix_and_sorts_arguments():
    first = request(args={"b": 2, "a": 1})
    second = request(args={"a": 1, "b": 2})

    assert cache._cache_key(first) == cache._cache_key(second)
    assert cache._cache_key(first).startswith("get_file_content:")


def test_cache_key_skips_uncacheable_and_non_json_arguments():
    assert cache._cache_key(request(name="github_reviewer_unknown")) is None
    assert cache._cache_key(request(args={"value": object()})) is None


def test_cache_interceptor_bypasses_missing_or_invalid_cache():
    calls = 0

    async def handler(received):
        nonlocal calls
        calls += 1
        return received

    no_runtime = run(cache.mcp_result_cache_interceptor(request(), handler))
    invalid_cache = run(
        cache.mcp_result_cache_interceptor(
            request(context={"mcp_result_cache": []}), handler
        )
    )

    assert no_runtime.name == "github_reviewer_get_file_content"
    assert invalid_cache.name == "github_reviewer_get_file_content"
    assert calls == 2


def test_cache_interceptor_caches_success_and_reuses_it():
    cached = {}
    result = successful_result()
    calls = 0

    async def handler(_):
        nonlocal calls
        calls += 1
        return result

    first = run(
        cache.mcp_result_cache_interceptor(
            request(context={"mcp_result_cache": cached}), handler
        )
    )
    second = run(
        cache.mcp_result_cache_interceptor(
            request(context={"mcp_result_cache": cached}), handler
        )
    )

    assert first is result
    assert second is result
    assert calls == 1
    assert len(cached) == 1


def test_cache_interceptor_does_not_cache_errors():
    cached = {}
    error_result = CallToolResult(content=[], isError=True)
    calls = 0

    async def handler(_):
        nonlocal calls
        calls += 1
        return error_result

    run(
        cache.mcp_result_cache_interceptor(
            request(context={"mcp_result_cache": cached}), handler
        )
    )
    run(
        cache.mcp_result_cache_interceptor(
            request(context={"mcp_result_cache": cached}), handler
        )
    )

    assert calls == 2
    assert cached == {}


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
        "servers:\n  reviewer:\n    url: http://default:9001/mcp\n    timeout: 12\n"
    )
    monkeypatch.setattr(loader, "_REGISTRY_PATH", registry_file)
    monkeypatch.setenv("REVIEWER_MCP_URL", "http://override:9001/mcp")

    registry = loader._load_registry()
    assert registry == {
        "reviewer": MCPServer(url="http://override:9001/mcp", timeout=12)
    }


def test_load_mcp_tools_handles_empty_unknown_and_failure(monkeypatch):
    assert run(loader.aload_agent_mcp_tools([])) == []

    monkeypatch.setattr(loader, "_load_registry", dict)
    with pytest.raises(ValueError, match="Unknown MCP server"):
        run(loader.aload_agent_mcp_tools([AgentMCPServer(name="missing")]))

    monkeypatch.setattr(
        loader,
        "_load_registry",
        lambda: {"reviewer": MCPServer(url="http://reviewer/mcp")},
    )

    async def unavailable(**_):
        raise RuntimeError("offline")

    monkeypatch.setattr(loader, "load_mcp_tools", unavailable)
    assert run(loader.aload_agent_mcp_tools([AgentMCPServer(name="reviewer")])) == []


def test_load_mcp_tools_collects_tools(monkeypatch):
    monkeypatch.setattr(
        loader,
        "_load_registry",
        lambda: {"reviewer": MCPServer(url="http://reviewer/mcp")},
    )

    async def available(**_):
        return ["tool-1", "tool-2"]

    monkeypatch.setattr(loader, "load_mcp_tools", available)
    result = run(loader.aload_agent_mcp_tools([AgentMCPServer(name="reviewer")]))
    assert result == ["tool-1", "tool-2"]
