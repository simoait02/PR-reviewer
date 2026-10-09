from typing import Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel

from github_mcp_tools.domains.git_tools import (
    register_read_only_git_tools,
    validate_repository_paths,
)
from github_mcp_tools.sandbox import Sandbox

_SECURITY_RULES = "/opt/pr-reviewer/security-rules"


class SecurityCommandResponse(BaseModel):
    sandbox_id: str
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    status: Literal["succeeded", "failed"]


class ReadDiffResponse(SecurityCommandResponse):
    base_sha: str
    head_sha: str
    changed_files: list[str]
    diff: str


class ReadFileResponse(SecurityCommandResponse):
    head_sha: str
    path: str
    start_line: int
    end_line: int
    content: str


class SearchCodeResponse(SecurityCommandResponse):
    head_sha: str
    query: str
    paths: list[str]


class SemgrepScanResponse(SecurityCommandResponse):
    base_sha: str
    changed_files: list[str]
    profile: Literal["security", "auth", "input_validation"]


async def _run_security_command(
    sandbox_id: str,
    command: list[str],
) -> SecurityCommandResponse:
    sandbox = Sandbox.get_instance()
    exit_code, stdout, stderr = await sandbox.exec(
        sandbox_id,
        command,
        workdir="/workspace/repo",
        environment={"GIT_OPTIONAL_LOCKS": "0"},
    )
    return SecurityCommandResponse(
        sandbox_id=sandbox_id,
        command=command,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        status="succeeded" if exit_code == 0 else "failed",
    )


async def _run_semgrep(
    sandbox_id: str,
    base_sha: str,
    changed_files: list[str] | None,
    profile: Literal["security", "auth", "input_validation"],
) -> SemgrepScanResponse:
    files = changed_files or []
    targets = files or ["."]
    validate_repository_paths(targets)
    config = {
        "security": "auto",
        "auth": f"{_SECURITY_RULES}/auth.yml",
        "input_validation": f"{_SECURITY_RULES}/input-validation.yml",
    }[profile]
    command = [
        "semgrep",
        "scan",
        "--config",
        config,
        "--baseline-commit",
        base_sha,
        "--json",
        "--no-git-ignore",
        "--",
        *targets,
    ]
    result = await _run_security_command(sandbox_id, command)
    return SemgrepScanResponse(
        **result.model_dump(),
        base_sha=base_sha,
        changed_files=files,
        profile=profile,
    )


# --------------------------------------------------------------------- tools

mcp = FastMCP("github-security-tools")
register_read_only_git_tools(mcp)


@mcp.tool()
async def read_diff(
    sandbox_id: str,
    base_sha: str,
    head_sha: str,
    changed_files: list[str] | None = None,
    context_lines: int = 20,
) -> ReadDiffResponse:
    """Read the exact pull-request diff between two commits.

    Use this as the primary source for security review when the changed code
    must be inspected. The result compares the supplied base and head SHAs;
    it does not infer changes from the default branch or the current working
    tree.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        base_sha: Exact base commit SHA for the pull request.
        head_sha: Exact head commit SHA for the pull request.
        changed_files: Optional repository-relative files to restrict the
            diff. Leave unset to inspect the complete pull-request diff.
        context_lines: Number of unchanged lines around each change. Must not
            be negative; the default is 20.

    Returns:
        The diff, selected files, commit SHAs, command output, and explicit
        status. Treat a failed status or non-zero exit code as unavailable
        diff evidence.
    """
    if context_lines < 0:
        raise ToolError("context_lines must not be negative")
    files = changed_files or []

    command = [
        "git",
        "diff",
        "--no-ext-diff",
        f"--unified={context_lines}",
        base_sha,
        head_sha,
        "--",
        *(files or ["."]),
    ]
    result = await _run_security_command(sandbox_id, command)
    return ReadDiffResponse(
        **result.model_dump(),
        base_sha=base_sha,
        head_sha=head_sha,
        changed_files=files,
        diff=result.stdout,
    )


@mcp.tool()
async def read_file(
    sandbox_id: str,
    head_sha: str,
    path: str,
    start_line: int = 1,
    end_line: int | None = None,
) -> ReadFileResponse:
    """Read a line range from a source file at the pull-request head.

    Use this after the diff identifies a file that needs more context. Read
    only the relevant range when possible, and use the exact head SHA supplied
    by pull-request metadata so the content matches the reviewed revision.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        head_sha: Exact pull-request head commit SHA to inspect.
        path: Repository-relative source-file path. Do not use an absolute
            path or a path outside the checkout.
        start_line: One-based first line to return; defaults to 1.
        end_line: Optional one-based inclusive last line. Leave unset to read
            through the end of the file.

    Returns:
        The selected source content, line range, command output, and status.
        A failed status means the requested source was not established.
    """
    if start_line < 1 or (end_line is not None and end_line < start_line):
        raise ToolError("invalid source line range")

    command = ["git", "show", "--no-ext-diff", f"{head_sha}:{path}"]
    result = await _run_security_command(sandbox_id, command)
    lines = result.stdout.splitlines(keepends=True)
    selected_end = end_line or len(lines)
    content = "".join(lines[start_line - 1 : selected_end])
    return ReadFileResponse(
        **result.model_dump(),
        head_sha=head_sha,
        path=path,
        start_line=start_line,
        end_line=min(selected_end, len(lines)),
        content=content,
    )


@mcp.tool()
async def search_code(
    sandbox_id: str,
    head_sha: str,
    query: str,
    paths: list[str] | None = None,
    regex: bool = False,
) -> SearchCodeResponse:
    """Search source code at the pull-request head without executing it.

    Use this to locate symbols, configuration, dangerous sinks, or references
    before reading specific files. Start with a focused literal query; enable
    regular expressions only when the search requires a pattern.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        head_sha: Exact pull-request head commit SHA to search.
        query: Non-empty text or extended regular expression to find.
        paths: Optional repository-relative paths to restrict the search.
        regex: When true, interpret ``query`` as an extended regular
            expression; otherwise search for literal text.

    Returns:
        Matching search output, query metadata, command status, and paths.
        Check the exit code because no matches and a failed search are
        different outcomes.
    """
    if not query.strip():
        raise ToolError("query must not be empty")
    search_paths = paths or []
    search_mode = "--extended-regexp" if regex else "--fixed-strings"
    command = [
        "git",
        "grep",
        "--no-ext-grep",
        "-n",
        "-I",
        search_mode,
        "-e",
        query,
        head_sha,
        "--",
        *(search_paths or ["."]),
    ]
    result = await _run_security_command(sandbox_id, command)
    return SearchCodeResponse(
        **result.model_dump(),
        head_sha=head_sha,
        query=query,
        paths=search_paths,
    )


@mcp.tool()
async def run_semgrep_security_scan(
    sandbox_id: str,
    base_sha: str,
    changed_files: list[str] | None = None,
) -> SemgrepScanResponse:
    """Scan pull-request changes for security findings introduced by the PR.

    Use this for broad security coverage after the exact base and head source
    are available. The scan compares against ``base_sha`` and should be
    treated as supporting evidence, not as a complete manual security review.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        base_sha: Exact base commit SHA used as the Semgrep baseline.
        changed_files: Optional repository-relative files to restrict the
            scan. Leave unset to scan the repository changes broadly.

    Returns:
        Semgrep output, selected files, baseline SHA, command status, and the
        security profile used. Check the status and interpret findings only in
        the context of the actual pull-request diff.
    """
    return await _run_semgrep(sandbox_id, base_sha, changed_files, "security")


@mcp.tool()
async def check_auth_coverage(
    sandbox_id: str,
    base_sha: str,
    changed_files: list[str] | None = None,
) -> SemgrepScanResponse:
    """Find changed web entry points that require authorization review.

    Use this to identify authentication or authorization boundaries that need
    manual inspection. It is a coverage aid, not proof that an authorization
    vulnerability exists.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        base_sha: Exact base commit SHA used to identify introduced findings.
        changed_files: Optional repository-relative files to restrict the
            check. Leave unset to inspect all pull-request changes.

    Returns:
        Semgrep coverage output and command status. Review every reported
        entry against the actual diff before publishing a finding.
    """
    return await _run_semgrep(sandbox_id, base_sha, changed_files, "auth")


@mcp.tool()
async def check_input_validation(
    sandbox_id: str,
    base_sha: str,
    changed_files: list[str] | None = None,
) -> SemgrepScanResponse:
    """Find changed untrusted-input paths that require validation review.

    Use this to identify input sources and potentially dangerous sinks for
    manual analysis of validation, injection, traversal, or deserialization
    risks. A match indicates a review target, not a confirmed vulnerability.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository.
        base_sha: Exact base commit SHA used to identify introduced findings.
        changed_files: Optional repository-relative files to restrict the
            check. Leave unset to inspect all pull-request changes.

    Returns:
        Semgrep coverage output and command status. Confirm each result using
        the pull-request diff and source before reporting a security finding.
    """
    return await _run_semgrep(
        sandbox_id,
        base_sha,
        changed_files,
        "input_validation",
    )
