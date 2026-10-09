from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver

from agents.internal.base import BaseAgent
from agents.internal.protocol import AgentRequest, AgentRuntimeContext
from agents.mcp.loader import aload_agent_mcp_tools
from agents.orchestrator.schemas import OrchestratorConfig, OrchestratorResponse


class ToolErrorsAsObservations(AgentMiddleware):
    """Return tool failures to the model as tool messages instead of raising."""

    @staticmethod
    def _error_message(request, exc: Exception) -> ToolMessage:
        name = request.tool_call["name"]
        return ToolMessage(
            content=(
                f"Tool `{name}` failed: {exc}\n"
                "Decide whether to retry with different arguments, continue "
                "without this result, or report the limitation."
            ),
            tool_call_id=request.tool_call["id"],
            name=name,
            status="error",
        )

    def wrap_tool_call(self, request, handler):
        try:
            return handler(request)
        except Exception as exc:  # noqa: BLE001 - expose tool failures to the model
            return self._error_message(request, exc)

    async def awrap_tool_call(self, request, handler):
        try:
            return await handler(request)
        except Exception as exc:  # noqa: BLE001 - expose tool failures to the model
            return self._error_message(request, exc)


class BaseOrchestrator:
    name: str = "orchestrator"

    def __init__(
        self,
        model: BaseChatModel,
        config: OrchestratorConfig,
        agents: Sequence[BaseAgent],
        checkpointer: BaseCheckpointSaver | None = None,
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
            middleware=[ToolErrorsAsObservations()],
        )
        return self._graph

    async def ainvoke_raw(
        self,
        request: AgentRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
    ) -> dict[str, Any]:
        graph = await self.abuild()

        message = HumanMessage(content=self._render_request(request))
        return await graph.ainvoke(
            {
                "messages": [message],
            },
            context={"github_token": github_token},
            config={"configurable": {"thread_id": thread_id}},
        )

    async def ainvoke_structured(
        self,
        request: AgentRequest,
        github_token: str | None = None,
        *,
        thread_id: str,
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
