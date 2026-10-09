from __future__ import annotations

from agents.internal.config import load_agent_yaml
from agents.internal.model_factory import build_chat_model
from agents.synthesizer.schema import SynthesizerRequest, SynthesizerResponse
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage


class Synthesizer:
    def __init__(self, model: BaseChatModel | None = None):
        config = load_agent_yaml(type(self))

        self.model = model or build_chat_model(config.model)
        self.system_prompt = config.system_prompt
        self.structured_model = self.model.with_structured_output(SynthesizerResponse)

    @classmethod
    def create_synthesizer(cls) -> Synthesizer:
        return cls()

    async def ainvoke_structured(
        self, request: SynthesizerRequest
    ) -> SynthesizerResponse:
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
        if isinstance(result, SynthesizerResponse):
            return result
        return SynthesizerResponse.model_validate(result)
