from __future__ import annotations

import inspect
from pathlib import Path

import yaml
from agents.mcp.config import AgentMCPServer
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    provider: str = "openai"
    name: str = "gpt-5.6-luna"
    temperature: float = 0.0
    use_responses_api: bool = False
    reasoning: str | None = None


class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    model: ModelConfig = Field(default_factory=ModelConfig)
    mcp_servers: list[AgentMCPServer] = Field(default_factory=list)


def load_agent_yaml(cls: type) -> AgentConfig:
    source_file = inspect.getfile(cls)
    yaml_path = Path(source_file).parent / "agent.yaml"

    with yaml_path.open() as f:
        raw_config = yaml.safe_load(f) or {}

    return AgentConfig.model_validate(raw_config)
