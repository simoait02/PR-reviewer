"""Domain-specific GitHub MCP servers."""

from fastmcp import FastMCP

from github_mcp_tools.domains import impact
from github_mcp_tools.domains import orchestrator
from github_mcp_tools.domains import reviewer
from github_mcp_tools.domains import security

DOMAINS: dict[str, FastMCP] = {
    "impact": impact.mcp,
    "orchestrator": orchestrator.mcp,
    "reviewer": reviewer.mcp,
    "security": security.mcp,
}

__all__ = ["DOMAINS", "impact", "orchestrator", "reviewer", "security"]
