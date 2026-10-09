from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, ClassVar

from agents.internal.config import load_agent_yaml
from agents.internal.model_factory import build_chat_model
from agents.internal.protocol import (
    AgentRequest,
    AgentResponse,
    AgentRuntimeContext,
)
from agents.mcp.loader import aload_agent_mcp_tools
from langchain.agents import create_agent
from langchain.tools import ToolRuntime
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool, StructuredTool


class BaseAgent(ABC):
    max_steps: ClassVar[int] = 6

    def __init__(
        self,
        model: BaseChatModel | None = None,
    ):
        self.config = load_agent_yaml(type(self))
        self.model = model or build_chat_model(self.config.model)
        self._graph = None

    @abstractmethod
    def get_tools(self) -> Sequence[BaseTool]:
        """Return tools implemented locally by this agent"""

    @staticmethod
    def _render_request(request: AgentRequest) -> str:
        parts = [
            f"Task objective:\n{request.task_objective}",
        ]
        if request.focus:
            focus = "\n".join(f"- {item}" for item in request.focus)
            parts.append(f"Focus and context:\n{focus}")
        return "\n\n".join(parts)

    async def abuild(self) -> Any:
        """build and cache the langgraph agent"""

        if self._graph is not None:
            return self._graph

        mcp_tools = await aload_agent_mcp_tools(self.config.mcp_servers)

        local_tools = list(self.get_tools())
        tools = [*local_tools, *mcp_tools]

        self._graph = create_agent(
            model=self.model,
            tools=tools,
            system_prompt=self.config.system_prompt,
            response_format=AgentResponse,
            name=self.config.name,
            context_schema=AgentRuntimeContext,
        )
        return self._graph

    async def ainvoke_raw(
        self,
        request: AgentRequest,
        context: AgentRuntimeContext | None = None,
    ) -> dict[str, Any]:
        graph = await self.abuild()

        message = HumanMessage(
            content=self._render_request(request),
        )

        return await graph.ainvoke(
            {
                "messages": [message],
            },
            context=context,
        )

    async def ainvoke_structured(
        self,
        request: AgentRequest,
        context: AgentRuntimeContext | None = None,
    ) -> AgentResponse:
        result = await self.ainvoke_raw(request, context=context)

        structured_response = result.get("structured_response")

        if structured_response is None:
            raise RuntimeError("Agent did not return a structured response")

        return AgentResponse.model_validate(structured_response)

    def as_tool(self) -> BaseTool:
        async def run_agent(runtime: ToolRuntime, **kwargs: Any) -> str:
            request: AgentRequest = AgentRequest.model_validate(kwargs)
            response = await self.ainvoke_structured(
                request,
                context=runtime.context,
            )
            return response.model_dump_json()

        return StructuredTool.from_function(
            coroutine=run_agent,
            name=self.config.name,
            description=self.config.description,
            args_schema=AgentRequest,
        )
