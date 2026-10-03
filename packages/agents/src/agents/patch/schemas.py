from pydantic import BaseModel, Field

from agents.internal.protocol import AgentStatus, ReviewFinding
from agents.orchestrator.schemas import OrchestratorResponse

PatchRequest = OrchestratorResponse


class PatchFinding(ReviewFinding):
    suggested_patch: str | None = Field(
        default=None,
        description=(
            "Optional suggested code change, preferably as a unified diff "
            "or a focused replacement snippet."
        ),
    )


class PatchResponse(BaseModel):
    status: AgentStatus = AgentStatus.COMPLETED
    summary: str
    patches: list[PatchFinding] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
