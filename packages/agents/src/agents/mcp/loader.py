import logging
import os
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import Any

import yaml
from agents.mcp.config import AgentMCPServer, MCPServer
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.interceptors import (
    MCPToolCallRequest,
    MCPToolCallResult,
)
from langchain_mcp_adapters.tools import load_mcp_tools

_REGISTRY_PATH = Path(__file__).parent / "servers.yaml"
logger = logging.getLogger(__name__)


from langchain.tools import ToolRuntime

def _runtime_github_token(runtime: ToolRuntime | None) -> str | None:
    if runtime is None:
        return None

    return runtime.context.get("github_token")


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


def _load_registry() -> dict[str, MCPServer]:
    with _REGISTRY_PATH.open() as f:
        raw_config: dict[str, Any] = yaml.safe_load(f) or {}

    raw_servers: dict[str, dict[str, Any]] = raw_config.get("servers", {})
    registry: dict[str, MCPServer] = {}

    for name, server_config in raw_servers.items():
        # Each registry entry can be overridden with <NAME>_MCP_URL.
        url_env_var = f"{name.upper()}_MCP_URL"
        server_config = {
            **server_config,
            "url": os.getenv(url_env_var, server_config["url"]),
        }
        registry[name] = MCPServer.model_validate(server_config)

    return registry


async def aload_agent_mcp_tools(
    servers: list[AgentMCPServer],
) -> list[BaseTool]:
    if not servers:
        return []

    registry = _load_registry()
    tools: list[BaseTool] = []
    for server in servers:
        curr_server = registry.get(server.name)
        if curr_server is None:
            raise ValueError(f"Unknown MCP server: {server.name}")
        connection = curr_server.model_dump()

        try:
            server_tools = await load_mcp_tools(
                session=None,
                connection=connection,
                tool_interceptors=[github_token_interceptor],
                server_name=server.name,
                tool_name_prefix=True,
            )
        except Exception:
            logger.warning(
                "MCP server '%s' is unavailable; continuing without its tools",
                server.name,
            )
            logger.debug(
                "MCP tool discovery failed for server '%s'",
                server.name,
                exc_info=True,
            )
            continue
        tools.extend(server_tools)
    return tools
