from typing import Any, Literal

from docker.errors import DockerException
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel

from github_mcp_tools.domains.common import (
    get_client,
    get_github_token,
)
from github_mcp_tools.sandbox import (
    CloneSandboxResponse,
    CreateSandboxResponse,
    DestroySandboxResponse,
    Sandbox,
    SandboxError,
)

mcp = FastMCP("github-orchestrator-tools")


class BuildCodeGraphResponse(BaseModel):
    sandbox_id: str
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    status: Literal["succeeded", "failed"]


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


@mcp.tool()
async def create_sandbox() -> CreateSandboxResponse:
    """Create and start an isolated Docker sandbox."""
    sandbox = Sandbox.get_instance()
    try:
        container_id = await sandbox.create_sandbox()
    except (DockerException, SandboxError) as exc:
        raise ToolError(f"Sandbox could not be created: {exc}") from exc

    return CreateSandboxResponse(sandbox_id=container_id, status="running")


@mcp.tool()
async def clone_sandbox_repository(
    sandbox_id: str,
    repository_owner: str,
    repository_name: str,
    pull_number: int,
    base_sha: str,
    head_sha: str,
) -> CloneSandboxResponse:
    """Clone the PR base and exact head commit into a created sandbox."""
    sandbox = Sandbox.get_instance()
    try:
        exit_code, stdout, stderr = await sandbox.clone(
            sandbox_id,
            repository_owner,
            repository_name,
            pull_number,
            base_sha,
            head_sha,
            access_token=get_github_token(),
        )
    except SandboxError as exc:
        raise ToolError(f"Repository could not be cloned: {exc}") from exc

    if exit_code != 0:
        detail = stderr or stdout or "git clone failed"
        raise ToolError(f"Repository could not be cloned: {detail}")

    return CloneSandboxResponse(
        sandbox_id=sandbox_id,
        repository_owner=repository_owner,
        repository_name=repository_name,
        pull_number=pull_number,
        base_sha=base_sha,
        head_sha=head_sha,
        path="/workspace/repo",
        status="cloned",
    )


@mcp.tool()
async def build_code_graph(sandbox_id: str) -> BuildCodeGraphResponse:
    """Build or update the code graph for the cloned repository."""
    sandbox = Sandbox.get_instance()

    exit_code, stdout, stderr = await sandbox.exec(
        sandbox_id,
        ["code-review-graph", "build"],
        workdir="/workspace/repo",
        environment={
            "CRG_DATA_DIR": "/workspace/.pr-review/code-review-graph",
        },
    )
    return BuildCodeGraphResponse(
        sandbox_id=sandbox_id,
        command=["code-review-graph", "build"],
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        status="succeeded" if exit_code == 0 else "failed",
    )


@mcp.tool()
async def destroy_sandbox(sandbox_id: str) -> DestroySandboxResponse:
    """Destroy a sandbox previously created by the orchestrator."""
    sandbox = Sandbox.get_instance()

    try:
        destroyed = await sandbox.destroy_sandbox(sandbox_id)
    except (DockerException, SandboxError) as exc:
        raise ToolError(f"Sandbox could not be destroyed: {exc}") from exc

    return DestroySandboxResponse(
        sandbox_id=sandbox_id,
        status="destroyed" if destroyed else "not_found",
    )
