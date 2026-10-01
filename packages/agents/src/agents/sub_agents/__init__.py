from agents.internal.base import BaseAgent
from agents.sub_agents.reviewer.agent import ReviewerAgent

AGENT_MAP: dict[str, type[BaseAgent]] = {
    "reviewer": ReviewerAgent,
}
