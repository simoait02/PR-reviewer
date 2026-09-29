from langchain_core.language_models import BaseChatModel
from pydantic import Field, BaseModel

from agents.mcp.config import AgentMCPServer


class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    mcp_servers: list[AgentMCPServer] = Field(default_factory=list)
