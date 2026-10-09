from fastmcp.exceptions import ToolError
from pydantic import BaseModel

from github_mcp_tools.infrastructure.sandbox import Sandbox
from pr_logging.core import get_logger

WORKDIR = "/workspace/repo"
MAX_OUTPUT_CHARS = 100_000

GIT_ENV = {
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_PAGER": "cat",
    "GIT_LITERAL_PATHSPECS": "1",
}
logger = get_logger(__name__)


class GitResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str


async def git_status(
    sandbox_id: str,
    paths: list[str] | None = None,
) -> GitResult:
    """Inspect uncommitted changes in the sandbox repository.

    Use this when you need to know whether the checkout has modified or
    untracked files before or after a review operation. This is read-only and
    does not change the repository.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        paths: Optional repository-relative paths to restrict the status
            output. Leave unset to inspect the whole repository.

    Returns:
        Git status output with the command exit code, standard output, and
        standard error. A non-zero exit code means the status could not be
        established.
    """
    return await _run(
        sandbox_id,
        ["status", "--short", "--untracked-files=all"],
        paths=paths,
    )


async def git_ls_files(
    sandbox_id: str,
    paths: list[str] | None = None,
) -> GitResult:
    """List tracked files in the sandbox repository.

    Use this to confirm which repository files are tracked or to narrow the
    set of files that can be inspected. It does not read file contents and is
    read-only.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        paths: Optional repository-relative path prefixes to filter the list.
            Leave unset to list all tracked files.

    Returns:
        A Git result whose standard output contains the matching tracked file
        paths. Check the exit code before relying on the result.
    """
    return await _run(sandbox_id, ["ls-files"], paths=paths)


async def git_log(
    sandbox_id: str,
    revision: str = "HEAD",
    paths: list[str] | None = None,
    max_count: int = 50,
) -> GitResult:
    """Read recent commit summaries from the sandbox repository.

    Use this when commit history is needed to understand how a change evolved
    or to identify commits relevant to a specific path. This does not inspect
    the working tree or execute repository code.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        revision: Commit, branch, or tag from which to start the history.
            Defaults to ``HEAD``.
        paths: Optional repository-relative paths to limit the history.
        max_count: Maximum number of commit summaries to return. Must be
            greater than zero; the default is 50.

    Returns:
        A Git result containing one-line commit summaries. Check the exit code
        and stderr if the revision or path is invalid.
    """
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
    """Show a commit, Git object, or selected paths at a revision.

    Use this to inspect committed content or commit metadata when the exact
    revision is known. Prefer a more focused path list when only part of the
    revision is relevant.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        revision: Commit, tag, branch, or other Git revision to display.
        paths: Optional repository-relative paths to limit the output.

    Returns:
        A Git result containing the requested committed content or metadata.
        Check the exit code before treating the output as evidence.
    """
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
    """Compare repository revisions or inspect the working-tree diff.

    Use this to review changes. With no revisions, compare the working tree
    with the index; with one revision, compare that revision with the working
    tree; with two revisions, compare the two revisions. Restrict the result
    to specific paths when the full diff is unnecessary.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        revision: Optional first commit or revision to compare.
        compare_revision: Optional second revision. It requires ``revision``
            and is useful for comparing a pull-request base and head.
        paths: Optional repository-relative paths to restrict the diff.
        context_lines: Number of unchanged lines around each change. Must not
            be negative; the default is 20.

    Returns:
        A Git result containing the diff in standard output. A non-zero exit
        code means the comparison failed and the output is not reliable.
    """
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
    """Search committed source text at a specific revision.

    Use this to find symbols, configuration keys, call sites, or other text
    before reading a file or investigating a dependency. The search is
    read-only and does not execute repository code.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        pattern: Text to find. It must not be empty.
        revision: Commit, branch, or tag to search. Defaults to ``HEAD``.
        paths: Optional repository-relative paths to restrict the search.
        regex: When true, interpret ``pattern`` as an extended regular
            expression; otherwise search for the literal text.

    Returns:
        A Git result containing matching file and line information in standard
        output. Check the exit code because no matches and a failed search are
        different outcomes.
    """
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
    operation = args[0] if args else "unknown"

    logger.debug(
        "Running git operation '{}' in sandbox '{}' with {} revisions "
        "and {} paths",
        operation,
        sandbox_id,
        len(revisions),
        len(paths),
    )

    exit_code, stdout, stderr = await Sandbox.get_instance().exec(
        sandbox_id,
        command,
        workdir=WORKDIR,
        environment=GIT_ENV,
    )

    log_method = logger.debug if exit_code == 0 else logger.warning
    log_method(
        "Git operation '{}' completed with exit code {}, "
        "stdout={} chars, stderr={} chars",
        operation,
        exit_code,
        len(stdout),
        len(stderr),
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
