from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pr_logging.core import get_logger

from github_mcp_tools.rag.models import BestPracticeResult
from github_mcp_tools.rag.service import get_best_practices_retriever
from github_mcp_tools.tools.git import (
    register_read_only_git_tools,
)

mcp = FastMCP("github-reviewer-tools")
register_read_only_git_tools(mcp)
logger = get_logger(__name__)


@mcp.tool()
async def search_best_practices(
    query: str,
    limit: int = 5,
) -> list[BestPracticeResult]:
    """Search the engineering best-practices knowledge base for review guidance.

    Use this tool when a pull-request review question can be answered or
    informed by the project's documented engineering practices. Ask a focused
    question in natural language and describe the relevant behavior, risk, or
    technology. For example: ``"How should user-controlled file paths be
    validated?"`` or ``"What testing is expected for a database migration?"``

    Args:
        query: A specific review question or description of the change to
            investigate. Include important concepts such as the component,
            data flow, or suspected risk instead of using a vague query like
            ``"best practices"``.
        limit: Maximum number of ranked guidance chunks to return. Use a small
            value for a focused answer and a larger value when exploring a
            broad question. The valid range is 1 to 8; the default is 5.

    Returns:
        Relevant guidance chunks ranked by semantic similarity. Use these
        results as context for the review, not as proof that the pull request
        contains a defect; findings must still be supported by the pull
        request's actual code and diff.
    """
    if not query.strip():
        logger.warning("Rejected empty best-practices search query")
        raise ToolError("query must not be empty")
    if limit < 1:
        logger.warning(
            "Rejected best-practices search with invalid limit {}",
            limit,
        )
        raise ToolError("limit must be greater than zero")

    logger.info(
        "Searching best practices with limit {}",
        limit,
    )

    results = await get_best_practices_retriever().search(
        query=query,
        limit=limit,
    )

    logger.debug(
        "Best-practices search returned {} results",
        len(results),
    )

    return results
