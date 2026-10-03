from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from agents.internal.config import load_agent_yaml
from agents.patch.base import BasePatch


class Patch(BasePatch):
    name = "patch"

    def __init__(
        self,
        model: BaseChatModel | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
    ):
        config = load_agent_yaml(type(self))
        super().__init__(
            model=model
            or ChatOpenAI(
                model=config.model.name,
                temperature=config.model.temperature,
                use_responses_api=config.model.use_responses_api,
            ),
            config=config,
            checkpointer=checkpointer,
        )

    @classmethod
    async def create_patch(cls) -> Patch:
        config = load_agent_yaml(cls)
        return cls(
            model=ChatOpenAI(
                model=config.model.name,
                temperature=config.model.temperature,
                use_responses_api=config.model.use_responses_api,
            ),
            checkpointer=InMemorySaver(),
        )
