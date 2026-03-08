# -*- coding: utf-8 -*-
"""Agents package — Auto-registers all agent classes on import."""

from agents.controller_agent import ControllerAgent
from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAgent
from agents.content_agent import ContentAgent
from agents.publisher_agent import PublisherAgent
from agents.analytics_agent import AnalyticsAgent
from agents.memory_agent import MemoryAgent
from agents.automation_agent import AutomationAgent

__all__ = [
    "ControllerAgent",
    "ResearchAgent",
    "StrategyAgent",
    "ContentAgent",
    "PublisherAgent",
    "AnalyticsAgent",
    "MemoryAgent",
    "AutomationAgent",
]
