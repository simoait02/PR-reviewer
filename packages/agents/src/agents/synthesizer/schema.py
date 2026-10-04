from pydantic import BaseModel, Field

from agents.internal.protocol import AgentStatus
from agents.orchestrator.schemas import OrchestratorResponse
from agents.patch.schemas import PatchResponse, PatchFinding


class SynthesizerRequest(BaseModel):
    orchestrator_response: OrchestratorResponse
    patch_response: PatchResponse


class SynthesizerResponse(BaseModel):
    status: AgentStatus = AgentStatus.COMPLETED
    summary: str
    findings: list[PatchFinding] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)