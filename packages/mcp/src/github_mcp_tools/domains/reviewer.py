from typing import Any

from fastmcp import FastMCP

from github_mcp_tools.domains.common import get_client
from github_mcp_tools.github_requests import PRFile, PullRequest
from github_mcp_tools.rag.models import BestPracticeResult, Category
from github_mcp_tools.rag_service import get_best_practices_retriever

mcp = FastMCP("github-reviewer-tools")


@mcp.tool()
async def search_best_practices(
    query: str,
    category: Category | None = None,
    limit: int = 5,
) -> list[BestPracticeResult]:
    """
    Search engineering best-practice chunks relevant to the review question.
    If category is provided, use one of the exact available category values:
    architecture, code-quality, code-review, collaboration,
    delivery-and-operations, dependencies-and-supply-chain,
    documentation-and-team-practices, observability-and-reliability,
    project-management, project-readiness, requirements-and-planning,
    security-and-privacy, or testing.
    """
    if not query.strip():
        raise ValueError("query must not be empty")
    return await get_best_practices_retriever().search(
        query=query,
        category=category,
        limit=limit,
    )


@mcp.tool()
async def get_pr_files(
    pull_number: int, repository_owner: str, repository_name: str, page: int = 1
) -> dict[str, Any]:
    """
    Retrieve a paginated list of files changed by a pull request.

    The response includes ``items``, ``page``, and ``has_next_page``. Request
    another page only when ``has_next_page`` is true.
    """
    client = get_client(repository_owner, repository_name)
    file_page = await client.fetch_pr_files(pull_number, page)
    return file_page.model_dump(mode="json", exclude_none=True)


@mcp.tool()
async def get_diff_content(
    pr: PullRequest,
    file: PRFile,
    repository_owner: str,
    repository_name: str,
) -> dict[str, Any] | None:
    """Get the unified diff for one changed file."""
    client = get_client(repository_owner, repository_name)
    return await client.fetch_diff_content(pr, file)


def main() -> None:
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9001)
