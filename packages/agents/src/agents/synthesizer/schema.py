from agents.internal.protocol import AgentStatus
from agents.orchestrator.schemas import OrchestratorResponse
from agents.patch.schemas import PatchFinding, PatchResponse
from pydantic import BaseModel, Field


class SynthesizerRequest(BaseModel):
    orchestrator_response: OrchestratorResponse
    patch_response: PatchResponse


class SynthesizerResponse(BaseModel):
    status: AgentStatus = AgentStatus.COMPLETED
    summary: str
    findings: list[PatchFinding] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
