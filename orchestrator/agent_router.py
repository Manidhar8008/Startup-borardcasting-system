# -*- coding: utf-8 -*-
"""Agent Router — Routes pipeline steps to the correct agent.

Maps step names (e.g. 'research', 'strategy', 'content') to registered agents
via the agent_registry. The orchestrator calls route() to get the right agent
for each workflow step.
"""

import logging
from typing import Optional

from agents.base_agent import BaseAgent
from agents.agent_registry import get_agent, registered_names

logger = logging.getLogger("orchestrator")

# Map workflow step names → agent registry names
# This decouples workflow definitions from agent implementation details.
STEP_TO_AGENT = {
    "controller":        "controller",
    "intake":            "intake",
    "trend":             "trend",
    "topic_ranker":      "topic_ranker",
    "idea_generator":    "idea_generator",
    "research":          "research",
    "strategy":          "strategy",
    "content":           "content",
    "multiply":          "content",
    "review":            "review",
    "linkedin_writer":   "linkedin_writer",
    "twitter_writer":    "twitter_writer",
    "instagram_writer":  "instagram_writer",
    "youtube_writer":    "youtube_writer",
    "newsletter_writer": "newsletter_writer",
    "automation":        "automation",
    "publish":           "publisher",
    "analytics":         "analytics",
    "memory":            "memory",
}


class AgentRouter:
    """Routes a workflow step name to the correct agent instance."""

    def __init__(self, brand: str = "janani_ai"):
        self.brand = brand

    def route(self, step_name: str) -> BaseAgent:
        """Return an agent instance for the given workflow step.

        Args:
            step_name: A workflow step like 'research', 'strategy', etc.

        Returns:
            An instantiated BaseAgent subclass.

        Raises:
            KeyError: If no agent is mapped to this step.
        """
        agent_name = STEP_TO_AGENT.get(step_name)
        if agent_name is None:
            raise KeyError(
                f"No agent mapped to step '{step_name}'. "
                f"Known steps: {list(STEP_TO_AGENT.keys())}"
            )
        agent = get_agent(agent_name, brand=self.brand)
        logger.info("Routed step '%s' → agent '%s'", step_name, agent.name)
        return agent

    def available_steps(self):
        """Return list of all routable step names."""
        return list(STEP_TO_AGENT.keys())

    def validate_pipeline(self, steps: list) -> list:
        """Check which steps in a pipeline are valid. Returns list of invalid ones."""
        return [s for s in steps if s not in STEP_TO_AGENT]
