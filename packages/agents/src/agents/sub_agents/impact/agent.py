from collections.abc import Sequence

from agents.internal.base import BaseAgent
from langchain_core.tools import BaseTool


class Impact(BaseAgent):
    def get_tools(self) -> Sequence[BaseTool]:
        """
        Return tools implemented locally by the impact agent.
        GitHub tools are MCP tools and are loaded by ``BaseAgent.abuild``
        according to the agent's ``mcp_servers`` declaration.
        """
        return []
