import pytest
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
from agents.sub_agents.patch.agent import PatchAgent
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
    assert config.use_responses_api is True


def test_load_agent_yaml_reads_each_agent_configuration():
    orchestrator_config = CodeReviewOrchestrator._load_config()
    assert orchestrator_config.name == "code_review_orchestrator"
    assert orchestrator_config.system_prompt
    assert orchestrator_config.sub_agents == ["reviewer", "impact", "patch"]

    for agent_type, expected_name in (
        (PatchAgent, "patch"),
        (Synthesizer, "synthesizer"),
    ):
        config = load_agent_yaml(agent_type)
        assert isinstance(config, AgentConfig)
        assert config.name == expected_name
        assert config.system_prompt


def test_patch_is_registered_as_a_standard_subagent():
    assert AGENT_MAP["patch"] is PatchAgent
    assert PatchAgent(model=object()).get_tools() == []


def test_agent_config_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        AgentConfig.model_validate({})
