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
    """Read the exact PR diff between the base and head commits."""
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
    """Read a source file from the checked-out PR head."""
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
    """Search source code at the PR head without executing repository code."""
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
    """Run Semgrep security rules only for findings introduced by the PR."""
    return await _run_semgrep(sandbox_id, base_sha, changed_files, "security")


@mcp.tool()
async def check_auth_coverage(
    sandbox_id: str,
    base_sha: str,
    changed_files: list[str] | None = None,
) -> SemgrepScanResponse:
    """Find web entry points that require manual authorization review."""
    return await _run_semgrep(sandbox_id, base_sha, changed_files, "auth")


@mcp.tool()
async def check_input_validation(
    sandbox_id: str,
    base_sha: str,
    changed_files: list[str] | None = None,
) -> SemgrepScanResponse:
    """Find untrusted-input sources that require validation and sink review."""
    return await _run_semgrep(
        sandbox_id,
        base_sha,
        changed_files,
        "input_validation",
    )
