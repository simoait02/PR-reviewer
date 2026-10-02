"""Domain-specific GitHub MCP servers."""

from fastmcp import FastMCP

from github_mcp_tools.domains import orchestrator, reviewer

DOMAINS: dict[str, FastMCP] = {
    "orchestrator": orchestrator.mcp,
    "reviewer": reviewer.mcp,
}

__all__ = ["DOMAINS", "orchestrator", "reviewer"]
