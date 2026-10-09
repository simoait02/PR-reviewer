from __future__ import annotations

from agents.internal.config import load_agent_yaml
from agents.internal.model_factory import build_chat_model
from agents.synthesizer.schema import SynthesizerRequest, SynthesizerResponse
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pr_logging.core import get_logger

logger = get_logger(__name__)


class Synthesizer:
    def __init__(self, model: BaseChatModel | None = None):
        config = load_agent_yaml(type(self))

        self.name = config.name
        self.model = model or build_chat_model(config.model)
        self.system_prompt = config.system_prompt
        self.structured_model = self.model.with_structured_output(SynthesizerResponse)

        logger.debug(
            "Initialized synthesizer '{}'",
            self.name,
        )

    @classmethod
    def create_synthesizer(cls) -> Synthesizer:
        logger.info("Creating synthesizer")
        synthesizer = cls()

        logger.info(
            "Created synthesizer '{}'",
            synthesizer.name,
        )

        return synthesizer

    async def ainvoke_structured(
        self, request: SynthesizerRequest
    ) -> SynthesizerResponse:
        logger.info(
            "Invoking synthesizer '{}'",
            self.name,
        )

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=(
                    "Orchestrator result:\n"
                    f"{request.orchestrator_response.model_dump_json(indent=2)}\n\n"
                    "Security feedback is included in the orchestrator result."
                )
            ),
        ]
        result = await self.structured_model.ainvoke(messages)

        response = (
            result
            if isinstance(result, SynthesizerResponse)
            else SynthesizerResponse.model_validate(result)
        )

        logger.debug(
            "Synthesizer '{}' completed with status '{}', {} findings, "
            "and {} limitations",
            self.name,
            response.status,
            len(response.findings),
            len(response.limitations),
        )

        return response
