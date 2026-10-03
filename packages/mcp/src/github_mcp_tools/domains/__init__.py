"""Domain-specific GitHub MCP servers."""

from fastmcp import FastMCP

from github_mcp_tools.domains import impact, orchestrator, patch, reviewer

DOMAINS: dict[str, FastMCP] = {
    "orchestrator": orchestrator.mcp,
    "reviewer": reviewer.mcp,
    "impact": impact.mcp,
    "patch": patch.mcp,
}

__all__ = ["DOMAINS", "impact", "orchestrator", "patch", "reviewer"]
