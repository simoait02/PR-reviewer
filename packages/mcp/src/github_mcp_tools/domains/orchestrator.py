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
    """Retrieve the authoritative metadata for a GitHub pull request.

    Use this as the first GitHub call when a review needs pull-request
    evidence. The response establishes the title, description, branches, base
    SHA, head SHA, and other metadata needed for later sandbox operations.

    Args:
        pull_number: Pull-request number in the repository.
        repository_owner: GitHub repository owner or organization.
        repository_name: GitHub repository name.

    Returns:
        Pull-request metadata as a dictionary. Confirm that the base and head
        SHAs are present before creating a sandbox or cloning source code.
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
    """Retrieve one paginated page of conversation comments on a pull request.

    Use this when discussion comments may clarify requirements, reported
    concerns, or requested changes. Fetch another page only when the response
    says that more pages are available.

    Args:
        pull_number: Pull-request number in the repository.
        repository_owner: GitHub repository owner or organization.
        repository_name: GitHub repository name.
        page: One-based page number to retrieve; defaults to 1.

    Returns:
        One page of comments and pagination metadata. Do not treat one page as
        the complete discussion unless the response confirms there is no next
        page.
    """
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
    """Retrieve one paginated page of submitted pull-request reviews.

    Use this to collect reviewer decisions, summaries, and requested changes
    that may affect the review context. Fetch later pages only when indicated
    by the returned pagination metadata.

    Args:
        pull_number: Pull-request number in the repository.
        repository_owner: GitHub repository owner or organization.
        repository_name: GitHub repository name.
        page: One-based page number to retrieve; defaults to 1.

    Returns:
        One page of submitted reviews and pagination metadata. A single page
        is not proof that all reviews have been retrieved.
    """
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
    """Retrieve one paginated page of inline file and line review comments.

    Use this when reviewer feedback is tied to a specific changed file or
    line. These comments can provide concrete review concerns or requirements
    for specialist analysis. Continue pagination only when requested by the
    response metadata.

    Args:
        pull_number: Pull-request number in the repository.
        repository_owner: GitHub repository owner or organization.
        repository_name: GitHub repository name.
        page: One-based page number to retrieve; defaults to 1.

    Returns:
        One page of inline review comments and pagination metadata. Preserve
        the file and line references when passing relevant comments onward.
    """
    client = get_client(repository_owner, repository_name)
    comment_page = await client.fetch_pr_review_comments(pull_number, page)
    return comment_page.model_dump(mode="json", exclude_none=True)


@mcp.tool()
async def create_sandbox() -> CreateSandboxResponse:
    """Create and start an isolated Docker sandbox for repository inspection.

    Use this only when the review needs source, diff, or code-graph evidence
    that is not available from GitHub metadata. Do not create a sandbox merely
    to complete a workflow step. The returned sandbox must be cloned before
    repository tools can be used, and it must be destroyed when all sandbox
    work is complete.

    Returns:
        A running sandbox ID. If creation fails, no repository evidence is
        available from the sandbox.
    """
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
    """Clone the pull request's exact base and head commits into a sandbox.

    Use this after ``get_pr_info`` confirms both commit SHAs and
    ``create_sandbox`` returns a running sandbox. The checkout is intended for
    trustworthy source and diff inspection, not for running arbitrary project
    commands.

    Args:
        sandbox_id: ID of a running sandbox created for this review.
        repository_owner: GitHub repository owner or organization.
        repository_name: GitHub repository name.
        pull_number: Pull-request number to clone.
        base_sha: Exact pull-request base commit SHA.
        head_sha: Exact pull-request head commit SHA.

    Returns:
        Clone status and the checked-out repository path. Confirm that the
        operation succeeded and that the returned head SHA matches the PR
        metadata before claiming repository inspection.
    """
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
    """Build the code graph used for downstream-impact analysis.

    Use this only after the repository has been cloned successfully and only
    when impact analysis is justified. The graph is stored inside the
    sandbox; this tool does not itself analyze callers or consumers.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.

    Returns:
        The executed command, exit code, output, and explicit succeeded or
        failed status. A failed graph build means graph-based impact evidence
        is unavailable.
    """
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
    """Clean up a sandbox after all repository analysis is complete.

    Use this as the final sandbox operation, including after a later clone,
    graph, or analysis step fails. Do not call it before all needed source and
    graph evidence has been collected.

    Args:
        sandbox_id: ID of the sandbox to destroy.

    Returns:
        Destruction status. ``destroyed`` confirms cleanup; ``not_found`` is
        acceptable when the sandbox has already disappeared.
    """
    sandbox = Sandbox.get_instance()

    try:
        destroyed = await sandbox.destroy_sandbox(sandbox_id)
    except (DockerException, SandboxError) as exc:
        raise ToolError(f"Sandbox could not be destroyed: {exc}") from exc

    return DestroySandboxResponse(
        sandbox_id=sandbox_id,
        status="destroyed" if destroyed else "not_found",
    )
