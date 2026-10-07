from enum import Enum
from typing import Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel

from github_mcp_tools.sandbox import Sandbox


class ReadOnlyGitCommand(str, Enum):
    BLAME = "blame"
    CAT_FILE = "cat-file"
    CHECK_ATTR = "check-attr"
    CHECK_IGNORE = "check-ignore"
    DESCRIBE = "describe"
    DIFF = "diff"
    DIFF_FILES = "diff-files"
    DIFF_INDEX = "diff-index"
    DIFF_TREE = "diff-tree"
    FOR_EACH_REF = "for-each-ref"
    GREP = "grep"
    LOG = "log"
    LS_FILES = "ls-files"
    LS_TREE = "ls-tree"
    NAME_REV = "name-rev"
    REV_LIST = "rev-list"
    REV_PARSE = "rev-parse"
    SHOW = "show"
    SHOW_REF = "show-ref"
    SHORTLOG = "shortlog"
    STATUS = "status"


READ_ONLY_GIT_BLOCKED_OPTIONS = {
    "--ext-diff",
    "--textconv",
    "--output",
    "-o",
}


class ExecuteGitCommandResponse(BaseModel):
    sandbox_id: str
    command: list[str]
    workdir: str
    exit_code: int
    stdout: str
    stderr: str
    status: Literal["succeeded", "failed"]


mcp = FastMCP("github-reviewer-tools")


@mcp.tool()
async def execute_git_command(
    sandbox_id: str,
    command: ReadOnlyGitCommand,
    args: list[str] | None = None,
    workdir: str = "/workspace/repo",
) -> ExecuteGitCommandResponse:
    """Execute a read-only Git command inside the reviewer sandbox."""
    sandbox = Sandbox.get_instance()

    if sandbox.container is None or sandbox.container.id != sandbox_id:
        raise ToolError("sandbox_id does not refer to the active sandbox")

    command_args = args or []
    has_blocked_option = any(
        argument in READ_ONLY_GIT_BLOCKED_OPTIONS
        or argument.startswith("--output=")
        or argument.startswith("-o")
        for argument in command_args
    )
    if has_blocked_option:
        raise ToolError(
            "the requested Git options are not allowed for read-only execution"
        )

    git_command = ["git", command.value, *command_args]
    exit_code, stdout, stderr = await sandbox.exec(
        git_command,
        workdir=workdir,
        environment={"GIT_OPTIONAL_LOCKS": "0"},
    )

    return ExecuteGitCommandResponse(
        sandbox_id=sandbox_id,
        command=git_command,
        workdir=workdir,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        status="succeeded" if exit_code == 0 else "failed",
    )
