from agents.mcp.config import AgentMCPServer
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    mcp_servers: list[AgentMCPServer] = Field(default_factory=list)
