import asyncio

from agents.synthesizer.agent import Synthesizer
from agents.synthesizer.schema import SynthesizerRequest, SynthesizerResponse
from langchain_core.messages import HumanMessage, SystemMessage

from .helpers import (
    make_orchestrator_response,
    make_synthesizer_response,
)


class FakeStructuredModel:
    def __init__(self, result):
        self.result = result
        self.messages = None

    async def ainvoke(self, messages):
        self.messages = messages
        return self.result


class FakeModel:
    def __init__(self, structured_model):
        self.structured_model = structured_model

    def with_structured_output(self, response_type):
        assert response_type is SynthesizerResponse
        return self.structured_model


def test_synthesizer_uses_stable_system_and_human_roles():
    expected = make_synthesizer_response()
    structured_model = FakeStructuredModel(expected)
    synthesizer = Synthesizer(model=FakeModel(structured_model))
    request = SynthesizerRequest(
        orchestrator_response=make_orchestrator_response(),
    )

    result = asyncio.run(synthesizer.ainvoke_structured(request))

    assert result == expected
    assert isinstance(structured_model.messages[0], SystemMessage)
    assert structured_model.messages[0].content == synthesizer.system_prompt
    assert isinstance(structured_model.messages[1], HumanMessage)
    assert "Orchestrator result:" in structured_model.messages[1].content
    assert "Security feedback is included" in structured_model.messages[1].content


def test_synthesizer_validates_mapping_results():
    expected = make_synthesizer_response()
    structured_model = FakeStructuredModel(expected.model_dump())
    synthesizer = Synthesizer(model=FakeModel(structured_model))

    result = asyncio.run(
        synthesizer.ainvoke_structured(
            SynthesizerRequest(
                orchestrator_response=make_orchestrator_response(),
            )
        )
    )

    assert result == expected
