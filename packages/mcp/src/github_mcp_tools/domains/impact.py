from typing import Any

from fastmcp import FastMCP

from github_mcp_tools.domains.common import get_client
from github_mcp_tools.github_requests import PRFile, PullRequest

mcp = FastMCP("github-impact-tools")


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
async def search_repository_code(
    query: str,
    repository_owner: str,
    repository_name: str,
    max_results: int = 20,
) -> dict[str, Any]:
    """Find repository files containing a symbol or code query.

    This returns compact matches with paths and blob SHAs. Fetch a matching
    file's content separately with ``get_file_content``. Results come from
    GitHub's indexed code search and may not represent the pull request head
    exactly; inspect ``incomplete_results`` and report that limitation.
    """
    client = get_client(repository_owner, repository_name)
    matches = await client.search_repository_code(query, max_results)
    return matches.model_dump(mode="json", exclude_none=True)


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
    """Fetch the complete UTF-8 text content of a GitHub file by its blob SHA.

    Use the ``sha`` returned by the pull request files endpoint. This returns
    the exact file version represented by that blob, including the post-change
    content of a modified or renamed file. The repository owner and name must
    match the repository that contains the blob. Binary files cannot be
    returned as text.
    """
    if not file_sha:
        raise ValueError("file_sha must not be empty")

    client = get_client(repository_owner, repository_name)
    return await client.fetch_file_blob(file_sha)
