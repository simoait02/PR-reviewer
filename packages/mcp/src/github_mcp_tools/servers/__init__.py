"""Domain-specific GitHub MCP servers."""

from fastmcp import FastMCP

from github_mcp_tools.servers import impact, orchestrator, reviewer, security

DOMAINS: dict[str, FastMCP] = {
    "impact": impact.mcp,
    "orchestrator": orchestrator.mcp,
    "reviewer": reviewer.mcp,
    "security": security.mcp,
}

__all__ = ["DOMAINS", "impact", "orchestrator", "reviewer", "security"]
