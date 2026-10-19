import os
from pathlib import Path
from typing import Any

import yaml
from agents.internal.middleware import (
    GithubTokenInterceptor,
    _runtime_github_token,
    github_token_interceptor,
)
from agents.mcp.config import AgentMCPServer, MCPServer
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.tools import load_mcp_tools
from pr_logging.core import get_logger

_REGISTRY_PATH = Path(__file__).parent / "servers.yaml"
logger = get_logger(__name__)

__all__ = [
    "GithubTokenInterceptor",
    "_runtime_github_token",
    "aload_agent_mcp_tools",
    "github_token_interceptor",
]


def _load_registry() -> dict[str, MCPServer]:
    logger.debug(
        "Loading MCP server registry from '{}'",
        _REGISTRY_PATH,
    )

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

    logger.debug(
        "Loaded {} MCP server definitions",
        len(registry),
    )

    return registry


async def aload_agent_mcp_tools(
    servers: list[AgentMCPServer],
) -> list[BaseTool]:
    if not servers:
        logger.debug("No MCP servers configured for agent")
        return []

    logger.debug(
        "Loading tools from {} MCP servers",
        len(servers),
    )

    registry = _load_registry()
    tools: list[BaseTool] = []
    for server in servers:
        curr_server = registry.get(server.name)
        if curr_server is None:
            logger.error(
                "MCP server '{}' is not registered",
                server.name,
            )
            raise ValueError(f"Unknown MCP server: {server.name}")

        logger.debug(
            "Connecting to MCP server '{}'",
            server.name,
        )
        connection = curr_server.model_dump()

        try:
            server_tools = await load_mcp_tools(
                session=None,
                connection=connection,
                tool_interceptors=[
                    github_token_interceptor,
                ],
                server_name=server.name,
                tool_name_prefix=True,
            )
        except Exception:  # noqa: BLE001
            logger.warning(
                "MCP server '{}' is unavailable; continuing without its tools",
                server.name,
            )
            logger.opt(exception=True).debug(
                "MCP tool discovery failed for server '{}'",
                server.name,
            )
            continue

        logger.debug(
            "Loaded {} tools from MCP server '{}'",
            len(server_tools),
            server.name,
        )
        tools.extend(server_tools)

    logger.info(
        "Loaded {} MCP tools from {} configured servers",
        len(tools),
        len(servers),
    )

    return tools
