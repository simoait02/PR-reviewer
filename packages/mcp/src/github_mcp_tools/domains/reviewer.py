from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from github_mcp_tools.domains.git_tools import (
    register_read_only_git_tools,
)
from github_mcp_tools.rag.models import BestPracticeResult, Category
from github_mcp_tools.rag_service import get_best_practices_retriever

mcp = FastMCP("github-reviewer-tools")
register_read_only_git_tools(mcp)


@mcp.tool()
async def search_best_practices(
    query: str,
    category: Category | None = None,
    limit: int = 5,
) -> list[BestPracticeResult]:
    """Retrieve relevant engineering guidance for the review question."""
    if not query.strip():
        raise ToolError("query must not be empty")
    if limit < 1:
        raise ToolError("limit must be greater than zero")

    return await get_best_practices_retriever().search(
        query=query,
        category=category,
        limit=limit,
    )
