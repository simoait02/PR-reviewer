from collections.abc import Sequence

from agents.internal.base import BaseAgent
from langchain_core.tools import BaseTool


class SecurityAgent(BaseAgent):
    def get_tools(self) -> Sequence[BaseTool]:
        """Return tools implemented locally by the security agent."""
        return []
