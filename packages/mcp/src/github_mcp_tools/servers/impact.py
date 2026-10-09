from enum import Enum
from typing import Literal

from fastmcp import FastMCP
from pydantic import BaseModel

from github_mcp_tools.tools.git import (
    register_read_only_git_tools,
)
from github_mcp_tools.infrastructure.sandbox import Sandbox
from pr_logging.core import get_logger

logger = get_logger(__name__)


class GraphQueryPattern(str, Enum):
    CALLERS_OF = "callers_of"
    REFERENCES_TO = "references_to"
    CALLEES_OF = "callees_of"
    IMPORTS_OF = "imports_of"
    IMPORTERS_OF = "importers_of"
    CHILDREN_OF = "children_of"
    TESTS_FOR = "tests_for"
    INHERITORS_OF = "inheritors_of"
    FILE_SUMMARY = "file_summary"


class CodeGraphResponse(BaseModel):
    sandbox_id: str
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    status: Literal["succeeded", "failed"]


class CodeGraphImpactResponse(CodeGraphResponse):
    base: str
    changed_files: list[str]
    max_depth: int


class CodeGraphQueryResponse(CodeGraphResponse):
    pattern: GraphQueryPattern
    target: str


async def _run_graph_command(
    sandbox_id: str,
    command: list[str],
) -> CodeGraphResponse:
    operation = command[1] if len(command) > 1 else "unknown"

    logger.debug(
        "Running code graph operation '{}' in sandbox '{}'",
        operation,
        sandbox_id,
    )

    sandbox = Sandbox.get_instance()
    exit_code, stdout, stderr = await sandbox.exec(
        sandbox_id,
        command,
        workdir="/workspace/repo",
        environment={
            "CRG_DATA_DIR": "/workspace/.pr-review/code-review-graph",
        },
    )

    log_method = logger.debug if exit_code == 0 else logger.warning
    log_method(
        "Code graph operation '{}' completed with exit code {}, "
        "stdout={} chars, stderr={} chars",
        operation,
        exit_code,
        len(stdout),
        len(stderr),
    )

    return CodeGraphResponse(
        sandbox_id=sandbox_id,
        command=command,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        status="succeeded" if exit_code == 0 else "failed",
    )


# --------------------------------------------------------------------- tools

mcp = FastMCP("github-impact-tools")
register_read_only_git_tools(mcp)


@mcp.tool()
async def get_code_graph_impact(
    sandbox_id: str,
    base: str,
    changed_files: list[str] | None = None,
    max_depth: int = 2,
) -> CodeGraphImpactResponse:
    """Analyze downstream consumers affected by pull-request changes.

    Use this after the repository has been cloned and the code graph has been
    built. It is appropriate when changed symbols, interfaces, modules, or
    files may affect callers, tests, or dependent components. Do not use it
    when no implementation evidence or changed files are available.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository
            and a successfully built code graph.
        base: Base commit or revision used to determine the pull-request
            changes.
        changed_files: Optional repository-relative files to scope the impact
            analysis. Leave unset to analyze all changes relative to ``base``.
        max_depth: Maximum dependency depth to follow. Use a smaller value for
            focused results and increase it only when deeper consumers matter.

    Returns:
        Impact-analysis output with the command status, changed files, and
        graph results. Check ``status`` and ``exit_code`` before using the
        output as evidence.
    """
    logger.info(
        "Starting code graph impact analysis in sandbox '{}' with {} "
        "changed files and max depth {}",
        sandbox_id,
        len(changed_files or []),
        max_depth,
    )

    command = ["code-review-graph", "impact"]
    if changed_files:
        command.extend(["--files", *changed_files])
    command.extend(["--depth", str(max_depth), "--base", base])

    result = await _run_graph_command(sandbox_id, command)
    logger.debug(
        "Completed code graph impact analysis in sandbox '{}' with status '{}'",
        sandbox_id,
        result.status,
    )

    return CodeGraphImpactResponse(
        **result.model_dump(),
        base=base,
        changed_files=changed_files or [],
        max_depth=max_depth,
    )


@mcp.tool()
async def query_code_graph(
    sandbox_id: str,
    pattern: GraphQueryPattern,
    target: str,
) -> CodeGraphQueryResponse:
    """Query relationships or summaries in the built repository code graph.

    Use this for a focused impact question after ``build_code_graph`` has
    succeeded. Choose the pattern that matches the relationship being tested,
    then provide the exact symbol, file, or target expected by that query.

    Args:
        sandbox_id: ID of a running sandbox containing the cloned repository
            and built code graph.
        pattern: Relationship to inspect, such as ``callers_of``,
            ``references_to``, ``callees_of``, ``imports_of``,
            ``importers_of``, ``children_of``, ``tests_for``,
            ``inheritors_of``, or ``file_summary``.
        target: Exact graph target, such as a symbol name or repository-
            relative file path, appropriate for the selected pattern.

    Returns:
        Query output with the selected pattern, target, command status, and
        graph results. A failed status means the query did not establish
        impact evidence.
    """
    logger.info(
        "Starting code graph query '{}' in sandbox '{}'",
        pattern.value,
        sandbox_id,
    )

    command = [
        "code-review-graph",
        "query",
        pattern.value,
        target,
    ]
    result = await _run_graph_command(sandbox_id, command)
    logger.debug(
        "Completed code graph query '{}' in sandbox '{}' with status '{}'",
        pattern.value,
        sandbox_id,
        result.status,
    )

    return CodeGraphQueryResponse(
        **result.model_dump(),
        pattern=pattern,
        target=target,
    )
