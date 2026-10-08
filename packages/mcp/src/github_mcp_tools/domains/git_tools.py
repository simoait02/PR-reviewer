from fastmcp.exceptions import ToolError
from pydantic import BaseModel

from github_mcp_tools.sandbox import Sandbox

WORKDIR = "/workspace/repo"
MAX_OUTPUT_CHARS = 100_000

GIT_ENV = {
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_PAGER": "cat",
    "GIT_LITERAL_PATHSPECS": "1",
}


class GitResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str


async def git_status(
    sandbox_id: str,
    paths: list[str] | None = None,
) -> GitResult:
    return await _run(
        sandbox_id,
        ["status", "--short", "--untracked-files=all"],
        paths=paths,
    )


async def git_ls_files(
    sandbox_id: str,
    paths: list[str] | None = None,
) -> GitResult:
    return await _run(sandbox_id, ["ls-files"], paths=paths)


async def git_log(
    sandbox_id: str,
    revision: str = "HEAD",
    paths: list[str] | None = None,
    max_count: int = 50,
) -> GitResult:
    _check_positive(max_count, "max_count")
    return await _run(
        sandbox_id,
        ["log", "--oneline", "--no-decorate", f"--max-count={max_count}"],
        revisions=[revision],
        paths=paths,
    )


async def git_show(
    sandbox_id: str,
    revision: str,
    paths: list[str] | None = None,
) -> GitResult:
    return await _run(
        sandbox_id,
        ["show", "--no-ext-diff", "--no-textconv"],
        revisions=[revision],
        paths=paths,
    )


async def git_diff(
    sandbox_id: str,
    revision: str | None = None,
    compare_revision: str | None = None,
    paths: list[str] | None = None,
    context_lines: int = 20,
) -> GitResult:
    if compare_revision and not revision:
        raise ToolError("revision is required when compare_revision is set")
    if context_lines < 0:
        raise ToolError("context_lines must not be negative")
    return await _run(
        sandbox_id,
        ["diff", "--no-ext-diff", "--no-textconv", f"--unified={context_lines}"],
        revisions=[r for r in (revision, compare_revision) if r],
        paths=paths,
    )


async def git_grep(
    sandbox_id: str,
    pattern: str,
    revision: str = "HEAD",
    paths: list[str] | None = None,
    regex: bool = False,
) -> GitResult:
    if not pattern:
        raise ToolError("pattern must not be empty")
    mode = "--extended-regexp" if regex else "--fixed-strings"
    return await _run(
        sandbox_id,
        ["grep", "-n", "-I", mode, "-e", pattern],
        revisions=[revision],
        paths=paths,
    )


async def _run(
    sandbox_id: str,
    args: list[str],
    revisions: list[str] | None = None,
    paths: list[str] | None = None,
) -> GitResult:
    revisions = revisions or []
    paths = paths or []

    for revision in revisions:
        _check_revision(revision)
    validate_repository_paths(paths)

    command = ["git", *args, *revisions, "--", *paths]
    exit_code, stdout, stderr = await Sandbox.get_instance().exec(
        sandbox_id,
        command,
        workdir=WORKDIR,
        environment=GIT_ENV,
    )
    return GitResult(
        exit_code=exit_code,
        stdout=_truncate(stdout),
        stderr=_truncate(stderr),
    )


def register_read_only_git_tools(mcp) -> None:
    for tool in (git_status, git_ls_files, git_log, git_show, git_diff, git_grep):
        mcp.tool()(tool)


def _check_revision(revision: str) -> None:
    if (
        not revision
        or revision.startswith("-")
        or any(character in revision for character in "\x00\r\n\t ")
    ):
        raise ToolError(f"invalid Git revision: {revision!r}")


def _check_path(path: str) -> None:
    if not path or path.startswith("/") or "\x00" in path or ".." in path.split("/"):
        raise ToolError(f"path must be repository-relative: {path!r}")


def validate_repository_paths(paths: list[str]) -> None:
    for path in paths:
        _check_path(path)


def _check_positive(value: int, name: str) -> None:
    if value < 1:
        raise ToolError(f"{name} must be greater than zero")


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + "\n... [output truncated]"
