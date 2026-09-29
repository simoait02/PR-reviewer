from enum import StrEnum

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    objective: str = Field(..., description="The task the agent must complete.")
    facts: list[str] = Field(
        default_factory=list, description="Known facts the agent can use."
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
    severity: ReviewSeverity
    filename: str
    line: int | None = None
    title: str
    explanation: str
    recommendation: str


class AgentResponse(BaseModel):
    status: AgentStatus = AgentStatus.COMPLETED
    summary: str
    findings: list[ReviewFinding] = Field(default_factory=list)
    approved: bool
