from agents.internal.protocol import (
    AgentRequest,
    AgentResponse,
    AgentStatus,
    ReviewFinding,
    ReviewSeverity,
)
from agents.orchestrator.schemas import OrchestratorResponse
from agents.synthesizer.schema import SynthesizerResponse


def make_request() -> AgentRequest:
    return AgentRequest(
        task_objective="Review the pull request",
        focus=["owner=acme", "repo=payments", "pull=42"],
    )


def make_finding(*, patch: str | None = None) -> ReviewFinding:
    return ReviewFinding(
        severity=ReviewSeverity.HIGH,
        filename="src/payment.py",
        line=42,
        title="Possible null access",
        explanation="The value can be absent before it is used.",
        recommendation="Check the value before using it.",
        suggested_patch=patch,
    )


def make_agent_response() -> AgentResponse:
    finding = make_finding()
    return AgentResponse(
        status=AgentStatus.COMPLETED,
        summary="The review completed.",
        findings=[
            ReviewFinding.model_validate(
                finding.model_dump(exclude={"suggested_patch"})
            )
        ],
        approved=False,
    )


def make_orchestrator_response() -> OrchestratorResponse:
    feedback = make_agent_response()
    return OrchestratorResponse(
        task_objective="Review the pull request",
        focus=["owner=acme", "repo=payments", "pull=42"],
        reviewer_feedback=feedback,
        impact_feedback=feedback,
        security_feedback=feedback,
    )


def make_synthesizer_response() -> SynthesizerResponse:
    return SynthesizerResponse(
        status=AgentStatus.COMPLETED,
        summary="The pull request contains one high-severity issue.",
        findings=[make_finding(patch="if value is not None:\n    process(value)")],
        limitations=["The full test suite was unavailable."],
    )
