from fastmcp import FastMCP

from github_mcp_tools.domains.git_tools import (
    ExecuteGitCommandResponse,
    ReadOnlyGitCommand,
    execute_read_only_git_command,
)


mcp = FastMCP("github-reviewer-tools")


@mcp.tool()
async def execute_git_command(
    sandbox_id: str,
    command: ReadOnlyGitCommand,
    args: list[str] | None = None,
    workdir: str = "/workspace/repo",
) -> ExecuteGitCommandResponse:
    """Execute a read-only Git command inside the reviewer sandbox."""
    return await execute_read_only_git_command(
        sandbox_id=sandbox_id,
        command=command,
        args=args,
        workdir=workdir,
    )
