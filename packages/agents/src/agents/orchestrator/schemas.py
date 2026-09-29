from enum import StrEnum
from typing import List

from pydantic import BaseModel, Field

from agents.mcp.config import AgentMCPServer


class Specialist(StrEnum):
    INTENT_MATCH = "intent_match"
    HISTORY = "history"
    IMPACT = "impact"

class ReviewPlan(BaseModel):
    needs_deep_review: bool
    applicable_specialists: List[Specialist] = Field(default_factory=list)
    reasoning:str

class OrchestratorConfig(BaseModel):
    name: str
    system_prompt: str
    sub_agents: list[str] = Field(default_factory=list)
    mcp_servers: list[AgentMCPServer] = Field(default_factory=list)
