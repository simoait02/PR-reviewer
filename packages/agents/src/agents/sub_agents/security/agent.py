from collections.abc import Sequence

from langchain_core.tools import BaseTool

from agents.internal.base import BaseAgent


class SecurityAgent(BaseAgent):
    def get_tools(self) -> Sequence[BaseTool]:
        """Return tools implemented locally by the security agent."""
        return []
