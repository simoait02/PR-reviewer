from agents.internal.protocol import AgentStatus, ReviewFinding
from agents.orchestrator.schemas import OrchestratorResponse
from pydantic import BaseModel, Field


class SynthesizerRequest(BaseModel):
    orchestrator_response: OrchestratorResponse


class SynthesizerResponse(BaseModel):
    status: AgentStatus = AgentStatus.COMPLETED
    summary: str
    findings: list[ReviewFinding] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
