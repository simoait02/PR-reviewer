from typing import Any

from fastmcp import FastMCP

from github_mcp_tools.domains.common import get_client

mcp = FastMCP("github-orchestrator-tools")


@mcp.tool()
async def get_pr_info(
    pull_number: int, repository_owner: str, repository_name: str
) -> dict[str, Any]:
    """
    Get the pull request title, description, base and head branches, and
    commit SHAs.
    """
    client = get_client(repository_owner, repository_name)
    pr = await client.fetch_pr_infos(pull_number)
    return pr.model_dump()


@mcp.tool()
async def get_pr_comments(
    pull_number: int,
    repository_owner: str,
    repository_name: str,
    page: int = 1,
) -> dict[str, Any]:
    """Retrieve one page of conversation comments on a pull request."""
    client = get_client(repository_owner, repository_name)
    comment_page = await client.fetch_pr_comments(pull_number, page)
    return comment_page.model_dump(mode="json", exclude_none=True)


@mcp.tool()
async def get_pr_reviews(
    pull_number: int,
    repository_owner: str,
    repository_name: str,
    page: int = 1,
) -> dict[str, Any]:
    """Retrieve one page of submitted reviews on a pull request."""
    client = get_client(repository_owner, repository_name)
    review_page = await client.fetch_pr_reviews(pull_number, page)
    return review_page.model_dump(mode="json", exclude_none=True)


@mcp.tool()
async def get_pr_review_comments(
    pull_number: int,
    repository_owner: str,
    repository_name: str,
    page: int = 1,
) -> dict[str, Any]:
    """Retrieve one page of inline file and line review comments."""
    client = get_client(repository_owner, repository_name)
    comment_page = await client.fetch_pr_review_comments(pull_number, page)
    return comment_page.model_dump(mode="json", exclude_none=True)


def main() -> None:
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)
