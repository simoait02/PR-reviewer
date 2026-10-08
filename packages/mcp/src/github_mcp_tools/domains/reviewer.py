from fastmcp import FastMCP

from github_mcp_tools.domains.git_tools import (
    register_read_only_git_tools,
)

mcp = FastMCP("github-reviewer-tools")
register_read_only_git_tools(mcp)
