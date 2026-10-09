from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from agents.internal.model_factory import build_chat_model
from agents.orchestrator.base import BaseOrchestrator
from agents.orchestrator.schemas import OrchestratorConfig
from agents.sub_agents import AGENT_MAP
from pr_logging.core import get_logger

logger = get_logger(__name__)


class CodeReviewOrchestrator(BaseOrchestrator):
    name = "code_review_orchestrator"

    def __init__(
        self,
        model: BaseChatModel,
        checkpointer: BaseCheckpointSaver | None = None,
    ):
        self.config = self._load_config()
        agents = [AGENT_MAP[name]() for name in self.config.sub_agents]

        super().__init__(
            model=model,
            config=self.config,
            agents=agents,
            checkpointer=checkpointer,
        )
        self.name = self.config.name

        logger.debug(
            "Initialized orchestrator '{}' with {} sub-agents",
            self.name,
            len(agents),
        )

    @staticmethod
    def _load_config() -> OrchestratorConfig:
        config_path = Path(__file__).with_name("agent.yaml")

        logger.debug(
            "Loading orchestrator configuration from '{}'",
            config_path,
        )

        with config_path.open() as f:
            raw_config: dict[str, Any] = yaml.safe_load(f) or {}

        config = OrchestratorConfig.model_validate(raw_config)

        logger.debug(
            "Loaded orchestrator configuration '{}' with {} sub-agents",
            config.name,
            len(config.sub_agents),
        )

        return config

    @classmethod
    async def create_orchestrator(cls) -> CodeReviewOrchestrator:
        logger.info("Creating code review orchestrator")

        config = cls._load_config()
        checkpointer = InMemorySaver()
        orchestrator = cls(
            model=build_chat_model(config.model),
            checkpointer=checkpointer,
        )

        logger.info(
            "Created code review orchestrator '{}'",
            orchestrator.name,
        )

        return orchestrator
