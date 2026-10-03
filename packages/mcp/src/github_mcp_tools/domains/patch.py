from typing import Any

from fastmcp import FastMCP

from github_mcp_tools.domains.common import get_client
from github_mcp_tools.github_requests import PRFile, PullRequest

mcp = FastMCP("github-patch-tools")


@mcp.tool()
async def get_pr_files(
    pull_number: int,
    repository_owner: str,
    repository_name: str,
    page: int = 1,
) -> dict[str, Any]:
    """Retrieve one page of files changed by a pull request."""
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
    """Get the unified diff for one changed pull-request file."""
    client = get_client(repository_owner, repository_name)
    return await client.fetch_diff_content(pr, file)


@mcp.tool()
async def get_file_content(
    file_sha: str,
    repository_owner: str,
    repository_name: str,
):
    """Fetch the complete text content of a GitHub file by blob SHA."""
    if not file_sha:
        raise ValueError("file_sha must not be empty")

    client = get_client(repository_owner, repository_name)
    return await client.fetch_file_blob(file_sha)
