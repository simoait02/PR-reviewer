from enum import Enum
from typing import Literal

from fastmcp import FastMCP
from pydantic import BaseModel

from github_mcp_tools.domains.git_tools import (
    register_read_only_git_tools,
)
from github_mcp_tools.sandbox import Sandbox


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
    sandbox = Sandbox.get_instance()
    exit_code, stdout, stderr = await sandbox.exec(
        sandbox_id,
        command,
        workdir="/workspace/repo",
        environment={
            "CRG_DATA_DIR": "/workspace/.pr-review/code-review-graph",
        },
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
    """Find the downstream impact of changed files from a PR base revision."""
    command = ["code-review-graph", "impact"]
    if changed_files:
        command.extend(["--files", *changed_files])
    command.extend(["--depth", str(max_depth), "--base", base])

    result = await _run_graph_command(sandbox_id, command)
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
    """Query callers, references, imports, tests, or summaries in the code graph."""
    command = [
        "code-review-graph",
        "query",
        pattern.value,
        target,
    ]
    result = await _run_graph_command(sandbox_id, command)
    return CodeGraphQueryResponse(
        **result.model_dump(),
        pattern=pattern,
        target=target,
    )
