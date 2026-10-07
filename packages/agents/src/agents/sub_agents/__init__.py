from agents.internal.base import BaseAgent
from agents.sub_agents.impact.agent import Impact
from agents.sub_agents.reviewer.agent import ReviewerAgent
from agents.sub_agents.security.agent import SecurityAgent

AGENT_MAP: dict[str, type[BaseAgent]] = {
    "impact": Impact,
    "reviewer": ReviewerAgent,
    "security": SecurityAgent,
}
