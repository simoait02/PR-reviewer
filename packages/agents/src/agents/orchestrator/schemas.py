from pydantic import BaseModel, Field

from agents.internal.config import ModelConfig
from agents.internal.protocol import AgentResponse
from agents.mcp.config import AgentMCPServer


class OrchestratorResponse(BaseModel):
    """Reviewer and impact output passed to the patch stage."""

    task_objective: str = Field(
        description="The task objective that the patch stage must continue.",
    )
    focus: list[str] = Field(
        default_factory=list,
        description="The confirmed pull request context for the patch stage.",
    )
    reviewer_feedback: AgentResponse
    impact_feedback: AgentResponse


class OrchestratorConfig(BaseModel):
    name: str
    system_prompt: str
    model: ModelConfig = Field(default_factory=ModelConfig)
    sub_agents: list[str] = Field(default_factory=list)
    mcp_servers: list[AgentMCPServer] = Field(default_factory=list)
