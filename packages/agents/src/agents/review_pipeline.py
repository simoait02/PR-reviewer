from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from pr_logging.core import get_logger

from agents.internal.protocol import AgentRequest
from agents.orchestrator.agent import CodeReviewOrchestrator
from agents.orchestrator.schemas import OrchestratorResponse
from agents.synthesizer.agent import Synthesizer
from agents.synthesizer.schema import SynthesizerRequest, SynthesizerResponse

logger = get_logger(__name__)


class ReviewPipelineState(TypedDict, total=False):
    request: AgentRequest
    thread_id: str
    orchestrator_response: OrchestratorResponse


class ReviewPipelineContext(TypedDict):
    github_token: str | None


class ReviewPipeline:
    def __init__(
        self,
        orchestrator: CodeReviewOrchestrator,
        synthesizer: Synthesizer,
    ):
        self.orchestrator = orchestrator
        self.synthesizer = synthesizer
        self._graph = None

        logger.debug("Initialized review pipeline")

    @classmethod
    async def create_pipeline(cls) -> ReviewPipeline:
        logger.info("Creating review pipeline")

        pipeline = cls(
            orchestrator=await CodeReviewOrchestrator.create_orchestrator(),
            synthesizer=Synthesizer.create_synthesizer(),
        )

        logger.info("Created review pipeline")

        return pipeline

    def abuild(self) -> Any:
        if self._graph is not None:
            logger.debug("Using cached review pipeline graph")
            return self._graph

        logger.info("Building review pipeline graph")

        graph = StateGraph(
            ReviewPipelineState,
            context_schema=ReviewPipelineContext,
            output_schema=SynthesizerResponse,
        )
        graph.add_node("orchestrator", self._run_orchestrator)
        graph.add_node("synthesizer", self._run_synthesizer)
        graph.add_edge(START, "orchestrator")
        graph.add_edge("orchestrator", "synthesizer")
        graph.add_edge("synthesizer", END)
        self._graph = graph.compile()

        logger.info("Built review pipeline graph")

        return self._graph

    async def _run_orchestrator(
        self,
        state: ReviewPipelineState,
        *,
        runtime: Runtime[ReviewPipelineContext],
    ) -> dict[str, OrchestratorResponse]:
        logger.debug("Running orchestrator pipeline stage")

        response = await self.orchestrator.ainvoke_structured(
            state["request"],
            github_token=runtime.context.get("github_token"),
            thread_id=state["thread_id"],
        )

        logger.debug(
            "Orchestrator pipeline stage completed: reviewer={}, impact={}, "
            "security={} findings",
            len(response.reviewer_feedback.findings),
            len(response.impact_feedback.findings),
            len(response.security_feedback.findings),
        )

        return {"orchestrator_response": response}

    async def _run_synthesizer(
        self,
        state: ReviewPipelineState,
    ) -> dict[str, Any]:
        logger.debug("Running synthesizer pipeline stage")

        response = await self.synthesizer.ainvoke_structured(
            SynthesizerRequest(
                orchestrator_response=state["orchestrator_response"],
            )
        )

        logger.debug(
            "Synthesizer pipeline stage completed with status '{}', "
            "{} findings, and {} limitations",
            response.status,
            len(response.findings),
            len(response.limitations),
        )

        return response.model_dump()

    async def ainvoke(
        self,
        request: AgentRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
    ) -> SynthesizerResponse:
        logger.info("Invoking review pipeline")

        graph = self.abuild()
        result = await graph.ainvoke(
            {
                "request": request,
                "thread_id": thread_id,
            },
            context={"github_token": github_token},
        )

        response = SynthesizerResponse.model_validate(result)

        logger.info(
            "Review pipeline completed with status '{}', {} findings, "
            "and {} limitations",
            response.status,
            len(response.findings),
            len(response.limitations),
        )

        return response

    async def astream(
        self,
        request: AgentRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        logger.info("Streaming review pipeline")

        graph = self.abuild()
        async for update in graph.astream(
            {
                "request": request,
                "thread_id": thread_id,
            },
            context={"github_token": github_token},
            stream_mode="updates",
        ):
            synthesizer_update = update.get("synthesizer")
            if synthesizer_update is not None:
                response = SynthesizerResponse.model_validate(synthesizer_update)

                logger.debug(
                    "Streaming pipeline update: status '{}', {} findings, "
                    "and {} limitations",
                    response.status,
                    len(response.findings),
                    len(response.limitations),
                )

                yield "status", {"status": response.status.value}
                yield "summary", {"summary": response.summary}

                for finding in response.findings:
                    yield "findings", finding.model_dump(mode="json")

                for limitation in response.limitations:
                    yield "limitations", {"limitation": limitation}
