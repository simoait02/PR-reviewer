import json
from collections.abc import Awaitable, Callable

from langchain_mcp_adapters.interceptors import (
    MCPToolCallRequest,
    MCPToolCallResult,
)
from mcp.types import CallToolResult

CACHEABLE_TOOLS = {
    "get_pr_files",
    "get_diff_content",
    "get_file_content",
    "search_repository_code",
}


def _cache_key(request: MCPToolCallRequest) -> str | None:
    tool_name = request.name.removeprefix(f"{request.server_name}_")
    if tool_name not in CACHEABLE_TOOLS:
        return None

    try:
        args = json.dumps(request.args, sort_keys=True)
    except (TypeError, ValueError):
        return None

    return f"{tool_name}:{args}"


async def mcp_result_cache_interceptor(
    request: MCPToolCallRequest,
    handler: Callable[
        [MCPToolCallRequest],
        Awaitable[MCPToolCallResult],
    ],
) -> MCPToolCallResult:
    runtime = request.runtime
    context = getattr(runtime, "context", None)
    if not isinstance(context, dict):
        return await handler(request)

    cache = context.get("mcp_result_cache")
    if not isinstance(cache, dict):
        return await handler(request)

    key = _cache_key(request)

    if key is None:
        return await handler(request)

    if key in cache:
        return cache[key]

    result = await handler(request)

    if isinstance(result, CallToolResult) and not result.isError:
        cache[key] = result

    return result
