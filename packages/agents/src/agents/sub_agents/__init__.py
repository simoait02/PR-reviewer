from agents.internal.base import BaseAgent
from agents.sub_agents.impact.agent import Impact
from agents.sub_agents.reviewer.agent import ReviewerAgent

AGENT_MAP: dict[str, type[BaseAgent]] = {
    "impact": Impact,
    "reviewer": ReviewerAgent,
}
