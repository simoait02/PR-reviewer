import pytest
from agents.internal import model_factory
from agents.internal.config import AgentConfig, ModelConfig, load_agent_yaml
from agents.internal.protocol import (
    AgentRequest,
    AgentResponse,
    AgentStatus,
    ReviewFinding,
    ReviewSeverity,
)
from agents.orchestrator.agent import CodeReviewOrchestrator
from agents.sub_agents import AGENT_MAP
from agents.sub_agents.security.agent import SecurityAgent
from agents.synthesizer.agent import Synthesizer
from pydantic import ValidationError


def test_agent_request_defaults_and_validation():
    request = AgentRequest(task_objective="Review the change")
    assert request.focus == []

    with pytest.raises(ValidationError):
        AgentRequest.model_validate({})


def test_review_models_use_safe_defaults():
    finding = ReviewFinding(
        filename="file.py",
        title="Issue",
        explanation="Explanation",
        recommendation="Recommendation",
    )
    response = AgentResponse(summary="Summary", findings=[finding], approved=True)

    assert finding.severity is ReviewSeverity.INFO
    assert response.status is AgentStatus.COMPLETED
    assert response.findings[0] == finding


def test_model_config_defaults_are_stable():
    config = ModelConfig()
    assert config.temperature == 0
    assert config.use_responses_api is False


def test_build_chat_model_uses_configured_openai_options(monkeypatch):
    captured = {}

    class FakeChatOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(model_factory, "ChatOpenAI", FakeChatOpenAI)

    result = model_factory.build_chat_model(
        ModelConfig(
            name="gpt-5.6-luna",
            temperature=0.2,
            reasoning="low",
        )
    )

    assert isinstance(result, FakeChatOpenAI)
    assert captured == {
        "model": "gpt-5.6-luna",
        "temperature": 0.2,
        "reasoning_effort": "low",
        "use_responses_api": True,
    }


def test_build_chat_model_rejects_unsupported_provider():
    with pytest.raises(ValueError, match="Unsupported model provider"):
        model_factory.build_chat_model(ModelConfig(provider="anthropic"))


def test_load_agent_yaml_reads_each_agent_configuration():
    orchestrator_config = CodeReviewOrchestrator._load_config()
    assert orchestrator_config.name == "code_review_orchestrator"
    assert orchestrator_config.system_prompt
    assert orchestrator_config.sub_agents == ["reviewer", "impact", "security"]

    for agent_type, expected_name in (
        (SecurityAgent, "security"),
        (Synthesizer, "synthesizer"),
    ):
        config = load_agent_yaml(agent_type)
        assert isinstance(config, AgentConfig)
        assert config.name == expected_name
        assert config.system_prompt


def test_security_is_registered_as_a_standard_subagent():
    assert AGENT_MAP["security"] is SecurityAgent
    assert SecurityAgent(model=object()).get_tools() == []


def test_agent_config_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        AgentConfig.model_validate({})
