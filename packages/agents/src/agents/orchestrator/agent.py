from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from agents.internal.base import BaseAgent
from agents.orchestrator.base import BaseOrchestrator
from agents.orchestrator.schemas import OrchestratorConfig


class CodeReviewOrchestrator(BaseOrchestrator):
    name = "code_review_orchestrator"

    def __init__(
        self,
        model: BaseChatModel,
        agents: Sequence[BaseAgent] = (),
    ):
        self.config = self._load_config()
        super().__init__(
            model=model,
            config=self.config,
            agents=agents or [],
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
        orchestrator = cls(model=ChatOpenAI(model="gpt-4o-mini", temperature=0))
        await orchestrator.abuild()
        return orchestrator
