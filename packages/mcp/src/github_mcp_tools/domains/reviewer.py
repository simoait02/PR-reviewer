from typing import Any

from fastmcp import FastMCP

from github_mcp_tools.domains.common import get_client
from github_mcp_tools.github_requests import PRFile, PullRequest


mcp = FastMCP("github-reviewer-tools")


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
