from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.interceptors import MCPToolCallResult
from langgraph.checkpoint.base import BaseCheckpointSaver

from agents.internal.base import BaseAgent
from agents.internal.protocol import AgentRequest, AgentRuntimeContext
from agents.mcp.loader import aload_agent_mcp_tools
from agents.orchestrator.schemas import OrchestratorConfig, OrchestratorResponse


class BaseOrchestrator:
    name: str = "orchestrator"

    def __init__(
        self,
        model: BaseChatModel,
        config: OrchestratorConfig,
        agents: Sequence[BaseAgent],
        checkpointer: BaseCheckpointSaver,
        extra_tools: Sequence[BaseTool] | None = None,
    ):
        self.model = model
        self.config = config
        self.agents = list(agents)
        self.system_prompt = config.system_prompt
        self.extra_tools = list(extra_tools or [])
        self.checkpointer = checkpointer
        self._graph = None

    async def abuild(self) -> Any:
        if self._graph is not None:
            return self._graph

        mcp_tools = await aload_agent_mcp_tools(self.config.mcp_servers)

        for agent in self.agents:
            await agent.abuild()

        agent_tools = [agent.as_tool() for agent in self.agents]

        tools = [
            *agent_tools,
            *self.extra_tools,
            *mcp_tools,
        ]
        self._graph = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=tools,
            response_format=OrchestratorResponse,
            name=self.name,
            context_schema=AgentRuntimeContext,
            checkpointer=self.checkpointer,
        )
        return self._graph

    async def ainvoke_raw(
        self,
        request: AgentRequest,
        thread_id: str,
        github_token: str | None = None,
    ) -> dict[str, Any]:
        graph = await self.abuild()

        message = HumanMessage(content=self._render_request(request))
        result_cache: dict[str, MCPToolCallResult] = {}
        try:
            return await graph.ainvoke(
                {
                    "messages": [message],
                },
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
        request: AgentRequest,
        thread_id: str,
        github_token: str | None = None,
    ) -> OrchestratorResponse:
        result = await self.ainvoke_raw(
            request, github_token=github_token, thread_id=thread_id
        )
        structured_response = result.get("structured_response")
        if structured_response is None:
            raise RuntimeError("Orchestrator did not return a structured response")
        return OrchestratorResponse.model_validate(structured_response)

    @staticmethod
    def _render_request(request: AgentRequest) -> str:
        parts = [
            f"Task objective: {request.task_objective}",
        ]

        if request.focus:
            focus = "\n".join(f"- {item}" for item in request.focus)
            parts.append(f"Focus and context:\n{focus}")

        return "\n\n".join(parts)
