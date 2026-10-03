from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.interceptors import MCPToolCallResult
from langgraph.checkpoint.base import BaseCheckpointSaver

from agents.internal.config import AgentConfig
from agents.internal.protocol import AgentRuntimeContext
from agents.mcp.loader import aload_agent_mcp_tools
from agents.patch.schemas import PatchRequest, PatchResponse


class BasePatch:
    def __init__(
        self,
        model: BaseChatModel,
        config: AgentConfig,
        checkpointer: BaseCheckpointSaver | None = None,
    ):
        self.model = model
        self.config = config
        self.system_prompt = config.system_prompt
        self.checkpointer = checkpointer
        self._graph = None

    async def abuild(self) -> Any:
        if self._graph is not None:
            return self._graph

        mcp_tools = await aload_agent_mcp_tools(self.config.mcp_servers)
        self._graph = create_agent(
            model=self.model,
            tools=mcp_tools,
            system_prompt=self.system_prompt,
            response_format=PatchResponse,
            name=self.config.name,
            context_schema=AgentRuntimeContext,
            checkpointer=self.checkpointer,
        )
        return self._graph

    async def ainvoke_raw(
        self,
        request: PatchRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
    ) -> dict[str, Any]:
        graph = await self.abuild()
        message = HumanMessage(content=self._render_request(request))
        result_cache: dict[str, MCPToolCallResult] = {}
        try:
            return await graph.ainvoke(
                {"messages": [message]},
                context={
                    "github_token": github_token,
                    "mcp_result_cache": result_cache,
                },
                config={"configurable": {"thread_id": thread_id}},
            )
        finally:
            result_cache.clear()

    async def ainvoke_structured(
        self,
        request: PatchRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
    ) -> PatchResponse:
        result = await self.ainvoke_raw(
            request,
            github_token=github_token,
            thread_id=thread_id,
        )
        structured_response = result.get("structured_response")
        if structured_response is None:
            raise RuntimeError("Patch chain did not return a structured response")
        return PatchResponse.model_validate(structured_response)

    @staticmethod
    def _render_request(request: PatchRequest) -> str:
        parts = [f"Task objective:\n{request.task_objective}"]

        if request.focus:
            focus = "\n".join(f"- {item}" for item in request.focus)
            parts.append(f"Focus and context:\n{focus}")

        parts.extend(
            [
                "Reviewer feedback:\n"
                + request.reviewer_feedback.model_dump_json(indent=2),
                "Impact feedback:\n"
                + request.impact_feedback.model_dump_json(indent=2),
            ]
        )
        return "\n\n".join(parts)
