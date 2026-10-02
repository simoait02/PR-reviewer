from pydantic import BaseModel, Field

from agents.internal.config import ModelConfig
from agents.mcp.config import AgentMCPServer


class OrchestratorResponse(BaseModel):
    """Structured final review returned to the API caller."""

    final_answer: str = Field(
        description=(
            "The final pull request feedback. Keep internal reasoning out of "
            "this field."
        )
    )


class OrchestratorConfig(BaseModel):
    name: str
    system_prompt: str
    model: ModelConfig = Field(default_factory=ModelConfig)
    sub_agents: list[str] = Field(default_factory=list)
    mcp_servers: list[AgentMCPServer] = Field(default_factory=list)
