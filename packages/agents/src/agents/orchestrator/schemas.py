from pydantic import BaseModel, Field

from agents.internal.config import ModelConfig
from agents.internal.protocol import AgentResponse
from agents.mcp.config import AgentMCPServer


class OrchestratorResponse(BaseModel):
    """Specialist output passed to the final synthesizer."""

    task_objective: str = Field(
        description="The task objective used by all review specialists.",
    )
    focus: list[str] = Field(
        default_factory=list,
        description="The confirmed pull request context for specialist stages.",
    )
    reviewer_feedback: AgentResponse
    impact_feedback: AgentResponse
    security_feedback: AgentResponse


class OrchestratorConfig(BaseModel):
    name: str
    system_prompt: str
    model: ModelConfig = Field(default_factory=ModelConfig)
    sub_agents: list[str] = Field(default_factory=list)
    mcp_servers: list[AgentMCPServer] = Field(default_factory=list)
