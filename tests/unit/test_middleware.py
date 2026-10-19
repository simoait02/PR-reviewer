import asyncio
from types import SimpleNamespace

from agents.internal.middleware import (
    SandboxMiddleware,
    _runtime_github_token,
)
from agents.internal.protocol import AgentRuntimeContext


class FakeRequest:
    def __init__(self, context, tool_call, tool):
        self.runtime = SimpleNamespace(context=context)
        self.tool_call = tool_call
        self.tool = tool

    def override(self, *, tool_call):
        return FakeRequest(self.runtime.context, tool_call, self.tool)


def test_sandbox_middleware_injects_only_tools_with_sandbox_id():
    context = AgentRuntimeContext(sandbox_id="sandbox-id")
    sandbox_tool = SimpleNamespace(args_schema={"properties": {"sandbox_id": {}}})
    metadata_tool = SimpleNamespace(args_schema={"properties": {"pull_number": {}}})

    sandbox_request = FakeRequest(
        context,
        {"name": "github_reviewer_git_status", "args": {}},
        sandbox_tool,
    )
    metadata_request = FakeRequest(
        context,
        {"name": "github_orchestrator_get_pr_info", "args": {}},
        metadata_tool,
    )

    injected = SandboxMiddleware._inject(sandbox_request)
    untouched = SandboxMiddleware._inject(metadata_request)

    assert injected.tool_call["args"] == {"sandbox_id": "sandbox-id"}
    assert untouched is metadata_request


def test_sandbox_middleware_remembers_created_sandbox():
    context = AgentRuntimeContext()
    request = FakeRequest(
        context,
        {"name": "github_orchestrator_create_sandbox", "args": {}},
        SimpleNamespace(args_schema={"properties": {}}),
    )
    result = SimpleNamespace(
        content='{"sandbox_id": "sandbox-id", "status": "running"}',
        status="success",
    )

    SandboxMiddleware._remember(request, result)

    assert context.sandbox_id == "sandbox-id"


def test_middleware_covers_context_and_tool_call_lifecycle_branches():
    context = AgentRuntimeContext(github_token="token")
    assert _runtime_github_token(SimpleNamespace(context=context)) == "token"

    no_sandbox = AgentRuntimeContext()
    no_tool_request = FakeRequest(
        no_sandbox,
        {"name": "tool", "args": {}},
        None,
    )
    assert SandboxMiddleware._inject(no_tool_request) is no_tool_request

    unrelated_request = FakeRequest(
        context,
        {"name": "other_tool", "args": {}},
        SimpleNamespace(args_schema={"properties": {}}),
    )
    SandboxMiddleware._remember(
        unrelated_request,
        SimpleNamespace(status="success", content="{}"),
    )
    assert context.sandbox_id is None

    failed_request = FakeRequest(
        context,
        {"name": "github_orchestrator_create_sandbox", "args": {}},
        SimpleNamespace(args_schema={"properties": {}}),
    )
    SandboxMiddleware._remember(
        failed_request,
        SimpleNamespace(status="error", content="{}"),
    )
    assert context.sandbox_id is None

    lifecycle_request = FakeRequest(
        context,
        {"name": "github_orchestrator_create_sandbox", "args": {}},
        SimpleNamespace(args_schema={"properties": {"sandbox_id": {}}}),
    )
    result = SimpleNamespace(
        status="success",
        content=[{"text": '{"sandbox_id": "new-sandbox"}'}],
    )

    assert SandboxMiddleware().wrap_tool_call(
        lifecycle_request,
        lambda request: result,
    ) is result
    assert context.sandbox_id == "new-sandbox"


def test_sandbox_middleware_async_wrap_tool_call():
    context = AgentRuntimeContext()
    request = FakeRequest(
        context,
        {"name": "other_tool", "args": {}},
        SimpleNamespace(args_schema={"properties": {}}),
    )
    result = SimpleNamespace(status="success", content="{}")

    async def handler(received_request):
        assert received_request is request
        return result

    assert asyncio.run(SandboxMiddleware().awrap_tool_call(request, handler)) is result
