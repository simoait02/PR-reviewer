from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from agents.orchestrator.base import BaseOrchestrator
from agents.orchestrator.schemas import OrchestratorConfig
from agents.sub_agents import AGENT_MAP


class CodeReviewOrchestrator(BaseOrchestrator):
    name = "code_review_orchestrator"

    def __init__(
        self,
        model: BaseChatModel,
    ):
        self.config = self._load_config()
        super().__init__(
            model=model,
            config=self.config,
            agents=[AGENT_MAP[name]() for name in self.config.sub_agents],
        )
        self.name = self.config.name

    @staticmethod
    def _load_config() -> OrchestratorConfig:
        config_path = Path(__file__).with_name("agent.yaml")

        with config_path.open() as f:
            raw_config: dict[str, Any] = yaml.safe_load(f) or {}
        return OrchestratorConfig.model_validate(raw_config)

    @classmethod
    async def create_orchestrator(cls) -> CodeReviewOrchestrator:
        config = cls._load_config()
        orchestrator = cls(
            model=ChatOpenAI(
                model=config.model.name,
                temperature=config.model.temperature,
                use_responses_api=config.model.use_responses_api,
            )
        )
        await orchestrator.abuild()
        return orchestrator
