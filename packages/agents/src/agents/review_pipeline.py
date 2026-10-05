from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from agents.internal.protocol import AgentRequest
from agents.orchestrator.agent import CodeReviewOrchestrator
from agents.orchestrator.schemas import OrchestratorResponse
from agents.patch.agent import Patch
from agents.patch.schemas import PatchResponse
from agents.synthesizer.agent import Synthesizer
from agents.synthesizer.schema import SynthesizerRequest, SynthesizerResponse


class ReviewPipelineState(TypedDict, total=False):
    request: AgentRequest
    thread_id: str
    orchestrator_response: OrchestratorResponse
    patch_response: PatchResponse


class ReviewPipelineContext(TypedDict):
    github_token: str | None


class ReviewPipeline:
    def __init__(
        self,
        orchestrator: CodeReviewOrchestrator,
        patch: Patch,
        synthesizer: Synthesizer,
    ):
        self.orchestrator = orchestrator
        self.patch = patch
        self.synthesizer = synthesizer
        self._graph = None

    @classmethod
    async def create_pipeline(cls) -> ReviewPipeline:
        return cls(
            orchestrator=await CodeReviewOrchestrator.create_orchestrator(),
            patch=await Patch.create_patch(),
            synthesizer=Synthesizer.create_synthesizer(),
        )

    def abuild(self) -> Any:
        if self._graph is not None:
            return self._graph

        graph = StateGraph(
            ReviewPipelineState,
            context_schema=ReviewPipelineContext,
            output_schema=SynthesizerResponse,
        )
        graph.add_node("orchestrator", self._run_orchestrator)
        graph.add_node("patch", self._run_patch)
        graph.add_node("synthesizer", self._run_synthesizer)
        graph.add_edge(START, "orchestrator")
        graph.add_edge("orchestrator", "patch")
        graph.add_edge("patch", "synthesizer")
        graph.add_edge("synthesizer", END)
        self._graph = graph.compile()
        return self._graph

    async def _run_orchestrator(
        self,
        state: ReviewPipelineState,
        *,
        runtime: Runtime[ReviewPipelineContext],
    ) -> dict[str, OrchestratorResponse]:
        response = await self.orchestrator.ainvoke_structured(
            state["request"],
            github_token=runtime.context.get("github_token"),
            thread_id=state["thread_id"],
        )
        return {"orchestrator_response": response}

    async def _run_patch(
        self,
        state: ReviewPipelineState,
        *,
        runtime: Runtime[ReviewPipelineContext],
    ) -> dict[str, PatchResponse]:
        response = await self.patch.ainvoke_structured(
            state["orchestrator_response"],
            github_token=runtime.context.get("github_token"),
            thread_id=f"{state['thread_id']}:patch",
        )
        return {"patch_response": response}

    async def _run_synthesizer(
        self,
        state: ReviewPipelineState,
    ) -> dict[str, Any]:
        response = await self.synthesizer.ainvoke_structured(
            SynthesizerRequest(
                orchestrator_response=state["orchestrator_response"],
                patch_response=state["patch_response"],
            )
        )
        return response.model_dump()

    async def ainvoke(
        self,
        request: AgentRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
    ) -> SynthesizerResponse:
        graph = self.abuild()
        result = await graph.ainvoke(
            {
                "request": request,
                "thread_id": thread_id,
            },
            context={"github_token": github_token},
        )

        return SynthesizerResponse.model_validate(result)

    async def astream(
        self,
        request: AgentRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
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
                yield "status", {"status": response.status.value}
                yield "summary", {"summary": response.summary}

                for finding in response.findings:
                    yield "findings", finding.model_dump(mode="json")

                for limitation in response.limitations:
                    yield "limitations", {"limitation": limitation}
