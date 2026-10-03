"""Domain-specific GitHub MCP servers."""

from fastmcp import FastMCP

from github_mcp_tools.domains import impact, orchestrator, reviewer

DOMAINS: dict[str, FastMCP] = {
    "orchestrator": orchestrator.mcp,
    "reviewer": reviewer.mcp,
    "impact": impact.mcp,
}

__all__ = ["DOMAINS", "impact", "orchestrator", "reviewer"]
