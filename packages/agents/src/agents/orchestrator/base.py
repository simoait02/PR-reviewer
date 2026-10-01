from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

from agents.internal.base import BaseAgent
from agents.internal.protocol import AgentRequest
from agents.mcp.loader import aload_agent_mcp_tools, github_token_context
from agents.orchestrator.schemas import OrchestratorConfig, OrchestratorResponse


class BaseOrchestrator:
    name: str = "orchestrator"

    def __init__(
        self,
        model: BaseChatModel,
        config: OrchestratorConfig,
        agents: Sequence[BaseAgent],
        extra_tools: Sequence[BaseTool] | None = None,
    ):
        self.model = model
        self.config = config
        self.agents = list(agents)
        self.system_prompt = config.system_prompt
        self.extra_tools = list(extra_tools or [])
        self._graph = None
        self._mcp_tools: list[BaseTool] | None = None

    async def abuild(self) -> Any:
        if self._graph is not None:
            return self._graph

        if self._mcp_tools is None:
            self._mcp_tools = await aload_agent_mcp_tools(self.config.mcp_servers)

        for agent in self.agents:
            await agent.abuild()

        agent_tools = [agent.as_tool() for agent in self.agents]

        tools = [
            *agent_tools,
            *self.extra_tools,
            *self._mcp_tools,
        ]
        self._graph = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=tools,
            response_format=OrchestratorResponse,
            name=self.name,
        )
        return self._graph

    async def ainvoke_raw(
        self,
        request: AgentRequest,
        github_token: str | None = None,
    ) -> dict[str, Any]:
        graph = await self.abuild()

        message = HumanMessage(content=self._render_request(request))
        token = github_token_context.set(github_token)
        try:
            return await graph.ainvoke(
                {
                    "messages": [message],
                }
            )
        finally:
            github_token_context.reset(token)

    async def ainvoke_structured(
        self,
        request: AgentRequest,
        github_token: str | None = None,
    ) -> OrchestratorResponse:
        result = await self.ainvoke_raw(
            request,
            github_token=github_token,
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
