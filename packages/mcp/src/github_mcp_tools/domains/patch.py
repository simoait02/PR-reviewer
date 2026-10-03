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
    """Retrieve one page of files changed by a pull request.

    Use this before inspecting a patch so the exact changed paths and blob
    SHAs are known. The response includes ``items``, ``page``, and
    ``has_next_page``. Request another page only when ``has_next_page`` is
    true. Use each item's ``sha`` with ``get_file_content`` to inspect the
    corresponding file version.
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
    """Get the unified diff for one changed pull-request file.

    Pass the pull-request metadata and the exact file record returned by
    ``get_pr_files``. The result contains the file's hunks and changed-line
    context as represented by GitHub. Use this together with the full blob
    content before proposing a focused patch. A missing or unsupported diff
    returns ``None``.
    """
    client = get_client(repository_owner, repository_name)
    return await client.fetch_diff_content(pr, file)


@mcp.tool()
async def get_file_content(
    file_sha: str,
    repository_owner: str,
    repository_name: str,
):
    """Fetch the complete UTF-8 text content of a GitHub file by blob SHA.

    Use the ``sha`` returned by ``get_pr_files``. This retrieves the exact
    file version represented by that blob, including the post-change content
    of a modified or renamed file. The repository owner and name must match
    the repository that contains the blob. Binary files cannot be returned as
    text. Inspect this content before generating a patch and never use it to
    modify the repository.
    """
    if not file_sha:
        raise ValueError("file_sha must not be empty")

    client = get_client(repository_owner, repository_name)
    return await client.fetch_file_blob(file_sha)
