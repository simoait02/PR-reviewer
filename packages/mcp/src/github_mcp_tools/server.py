import os
from typing import Any

from fastmcp import FastMCP

from github_mcp_tools.github_requests import GithubRequest, GithubClient, PullRequest, PRFile

github_request = GithubRequest(
    repository_owner=os.environ.get("GITHUB_REPO_OWNER", "kubernetes"),
    repository_name=os.environ.get("GITHUB_REPO_NAME", "kubernetes"),
    access_token=os.environ.get("GITHUB_TOKEN", ""),
)
client = GithubClient(github_request)

mcp = FastMCP("github-pr-tools")

@mcp.tool()
async def get_pr_info(pull_number: int) -> dict[str, Any]:
    """
    Get the pull request's title, description, base and head branch names,
    and their commit SHAs. The commit SHAs identify the exact base and head
    revisions of the pull request and can be used to retrieve or compare
    the changes introduced by the PR.
    """
    pr = await client.fetch_pr_infos(pull_number)
    return pr.model_dump()

@mcp.tool()
async def get_pr_comments(pull_number: int) -> list[dict[str, Any]]:
    """
    Retrieve all conversation comments on a pull request, including
    the author's username, comment body, creation timestamp, and
    author association.
    """
    pr = await client.fetch_pr_comments(pull_number)
    return [p.model_dump() for p in pr]

@mcp.tool()
async def get_pr_files(pull_number: int, page: int = 1) -> dict[str, Any]:
    """
    Retrieve a paginated list of files changed by a pull request.

    Each file includes its path, change status, additions, deletions,
    and patch when available. Use the patch to identify the changes
    introduced by the pull request. If the result contains 15 files,
    call this tool again with the next page number to retrieve more files.
    """
    files = await client.fetch_pr_files(pull_number, page)
    return {
        "files": [file.model_dump() for file in files],
        "page": page,
        "has_next_page": len(files) == 15,
    }

@mcp.tool()
async def get_diff_content(pr: PullRequest, file: PRFile) -> list[dict[str, Any]]:
    """
    Get the unified diff patch for one specific file changed in a pull
    request. Use `get_pr_files` first to see which filenames changed.
    """
    changes = await client.fetch_diff_content(pr,file)
    return changes


def main() -> None:
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)

if __name__ == "__main__":
    main()
