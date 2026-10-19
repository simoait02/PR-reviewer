from enum import StrEnum
from pydantic import BaseModel, Field


class AgentRuntimeContext(BaseModel):
    """Request-scoped values available to agent tools."""

    github_token: str | None = None
    sandbox_id: str | None = None


class AgentRequest(BaseModel):
    """Task envelope sent from the orchestrator to a specialist.

    The orchestrator turns one internal plan task into this request. Agents
    are stateless, so the task objective and focus required to complete that
    task travel with every call.
    """

    task_objective: str = Field(
        ...,
        description=(
            "One imperative sentence stating exactly what the specialist must "
            "do. Do not put the internal review plan here."
        ),
    )
    focus: list[str] = Field(
        default_factory=list,
        description=(
            "Confirmed pull request context and review areas the specialist "
            "must use. Do not include the internal plan or reasoning."
        ),
    )


class AgentStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    INPUT_REQUIRED = "input_required"


class ReviewSeverity(StrEnum):
    BLOCKER = "blocker"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ReviewFinding(BaseModel):
    severity: ReviewSeverity = Field(
        default=ReviewSeverity.INFO,
        description=(
            "Finding severity. Use info when the evidence does not support "
            "a stronger severity."
        ),
    )
    filename: str = Field(
        ...,
        description="Exact changed-file path from the GitHub file listing.",
    )
    line: int | None = Field(
        default=None,
        description="Changed-file line number when the finding is line-specific.",
    )
    title: str
    explanation: str
    recommendation: str
    suggested_patch: str | None = Field(
        default=None,
        description=(
            "Optional unified diff or focused replacement snippet proposed "
            "for this finding."
        ),
    )


class AgentResponse(BaseModel):
    """Typed specialist feedback consumed by the orchestrator.

    This response is never returned directly by the API. The orchestrator
    uses it to write the final pull request review.
    """

    status: AgentStatus = AgentStatus.COMPLETED
    summary: str
    findings: list[ReviewFinding] = Field(default_factory=list)
    approved: bool
