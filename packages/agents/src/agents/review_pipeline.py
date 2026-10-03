from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from agents.internal.protocol import AgentRequest
from agents.orchestrator.agent import CodeReviewOrchestrator
from agents.orchestrator.schemas import OrchestratorResponse
from agents.patch.agent import Patch
from agents.patch.schemas import PatchResponse


class ReviewPipelineState(TypedDict, total=False):
    request: AgentRequest
    thread_id: str
    orchestrator_response: OrchestratorResponse
    patch_response: PatchResponse


class ReviewPipelineContext(TypedDict):
    github_token: str | None


class ReviewPipelineOutput(TypedDict):
    orchestrator_response: OrchestratorResponse
    patch_response: PatchResponse


class ReviewPipeline:
    def __init__(
        self,
        orchestrator: CodeReviewOrchestrator,
        patch: Patch,
    ):
        self.orchestrator = orchestrator
        self.patch = patch
        self._graph = None

    @classmethod
    async def create_pipeline(cls) -> ReviewPipeline:
        return cls(
            orchestrator=await CodeReviewOrchestrator.create_orchestrator(),
            patch=await Patch.create_patch(),
        )

    def abuild(self) -> Any:
        if self._graph is not None:
            return self._graph

        graph = StateGraph(
            ReviewPipelineState,
            context_schema=ReviewPipelineContext,
        )
        graph.add_node("orchestrator", self._run_orchestrator)
        graph.add_node("patch", self._run_patch)
        graph.add_edge(START, "orchestrator")
        graph.add_edge("orchestrator", "patch")
        graph.add_edge("patch", END)
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

    async def ainvoke(
        self,
        request: AgentRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
    ) -> ReviewPipelineOutput:
        graph = self.abuild()
        result = await graph.ainvoke(
            {
                "request": request,
                "thread_id": thread_id,
            },
            context={"github_token": github_token},
        )

        return {
            "orchestrator_response": result["orchestrator_response"],
            "patch_response": result["patch_response"],
        }
