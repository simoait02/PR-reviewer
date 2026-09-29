import logging
import os
from pathlib import Path
from typing import Any

import yaml
from agents.mcp.config import AgentMCPServer, MCPServer
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.tools import load_mcp_tools

_REGISTRY_PATH = Path(__file__).parent / "servers.yaml"
logger = logging.getLogger(__name__)


def _load_registry() -> dict[str, MCPServer]:
    with _REGISTRY_PATH.open() as f:
        raw_config: dict[str, Any] = yaml.safe_load(f) or {}

    raw_servers: dict[str, dict[str, Any]] = raw_config.get("servers", {})
    registry: dict[str, MCPServer] = {}

    for name, server_config in raw_servers.items():
        # Example: the `github` entry can be overridden with GITHUB_MCP_URL.
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
            raise ValueError(
                f"Unknown MCP server: {server.name}"
            )

        try:
            server_tools = await load_mcp_tools(
                session=None,
                connection=curr_server.model_dump(),
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
