import json
from collections.abc import Awaitable, Callable

from langchain.agents.middleware import AgentMiddleware
from langchain.tools import ToolRuntime
from langchain_mcp_adapters.interceptors import (
    MCPToolCallRequest,
    MCPToolCallResult,
)


def _runtime_github_token(runtime: ToolRuntime | None) -> str | None:
    if runtime is None:
        return None

    if isinstance(runtime.context, dict):
        return runtime.context.get("github_token")
    return runtime.context.github_token


class GithubTokenInterceptor:
    """Forward the current request's GitHub token to the MCP server."""

    async def __call__(
        self,
        request: MCPToolCallRequest,
        handler: Callable[
            [MCPToolCallRequest],
            Awaitable[MCPToolCallResult],
        ],
    ) -> MCPToolCallResult:
        github_token = _runtime_github_token(request.runtime)
        if not github_token:
            return await handler(request)

        headers = {
            **(request.headers or {}),
            "X-GitHub-Token": github_token,
        }
        return await handler(request.override(headers=headers))


github_token_interceptor = GithubTokenInterceptor()


class SandboxMiddleware(AgentMiddleware):
    """Store the created sandbox and add it to tools that need it."""

    @staticmethod
    def _inject(request):
        sandbox_id = request.runtime.context.sandbox_id
        if not sandbox_id or request.tool is None:
            return request

        schema = request.tool.args_schema
        fields = (
            schema.get("properties", {})
            if isinstance(schema, dict)
            else schema.model_fields
        )
        if "sandbox_id" not in fields:
            return request

        return request.override(
            tool_call={
                **request.tool_call,
                "args": {
                    **request.tool_call.get("args", {}),
                    "sandbox_id": sandbox_id,
                },
            }
        )

    @staticmethod
    def _remember(request, result):
        if request.tool_call["name"] != "github_orchestrator_create_sandbox":
            return
        if getattr(result, "status", None) == "error":
            return

        content = result.content
        if isinstance(content, list):
            content = content[0].get("text", "")
        request.runtime.context.sandbox_id = json.loads(content)["sandbox_id"]

    def wrap_tool_call(self, request, handler):
        result = handler(self._inject(request))
        self._remember(request, result)
        return result

    async def awrap_tool_call(self, request, handler):
        result = await handler(self._inject(request))
        self._remember(request, result)
        return result
