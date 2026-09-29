from typing import Any

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from github_mcp_tools.github_requests import (
    GithubClient,
    GithubRequest,
    PRFile,
    PullRequest,
)


def get_github_token() -> str:
    headers = get_http_headers(include={"x-github-token"})
    return headers.get("x-github-token", "")

def get_client(
        repository_owner: str,
        repository_name: str,
)->GithubClient:
    return GithubClient(
        GithubRequest(
            repository_owner=repository_owner,
            repository_name=repository_name,
            access_token=get_github_token(),
        )
    )

mcp = FastMCP("github-pr-tools")


@mcp.tool()
async def get_pr_info(pull_number: int, repository_owner:str, repository_name: str) -> dict[str, Any]:
    """
    Get the pull request's title, description, base and head branch names,
    and their commit SHAs. The commit SHAs identify the exact base and head
    revisions of the pull request and can be used to retrieve or compare
    the changes introduced by the PR.
    """
    client = get_client(repository_owner, repository_name)
    pr = await client.fetch_pr_infos(pull_number)
    return pr.model_dump()


@mcp.tool()
async def get_pr_comments(pull_number: int, repository_owner:str, repository_name: str) -> list[dict[str, Any]]:
    """
    Retrieve all conversation comments on a pull request, including
    the author's username, comment body, creation timestamp, and
    author association.
    """
    client = get_client(repository_owner, repository_name)
    pr = await client.fetch_pr_comments(pull_number)
    return [p.model_dump() for p in pr]


@mcp.tool()
async def get_pr_files(pull_number: int, repository_owner:str, repository_name: str, page: int = 1) -> dict[str, Any]:
    """
    Retrieve a paginated list of files changed by a pull request.

    Each file includes its path, change status, additions, deletions,
    and patch when available. Use the patch to identify the changes
    introduced by the pull request. If the result contains 15 files,
    call this tool again with the next page number to retrieve more files.
    """
    client = get_client(repository_owner, repository_name)
    files = await client.fetch_pr_files(pull_number, page)
    return {
        "files": [file.model_dump() for file in files],
        "page": page,
        "has_next_page": len(files) == 15,
    }


@mcp.tool()
async def get_diff_content(pr: PullRequest, file: PRFile, repository_owner:str, repository_name: str) -> list[dict[str, Any]]:
    """
    Get the unified diff patch for one specific file changed in a pull
    request. Use `get_pr_files` first to see which filenames changed.
    """
    client = get_client(repository_owner, repository_name)
    changes = await client.fetch_diff_content(pr, file)
    return changes


def main() -> None:
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)


if __name__ == "__main__":
    main()
