# -*- coding: utf-8 -*-
"""Agents package — Auto-registers all agent classes on import."""

from agents.controller_agent import ControllerAgent
from agents.morning_intake_agent import MorningIntakeAgent
from agents.trend_agent import TrendAgent
from agents.topic_ranker import TopicRanker
from agents.idea_generator import IdeaGenerator
from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAgent
from agents.content_agent import ContentAgent
from agents.review_agent import ReviewAgent
from agents.publisher_agent import PublisherAgent
from agents.analytics_agent import AnalyticsAgent
from agents.memory_agent import MemoryAgent
from agents.automation_agent import AutomationAgent

# Platform-specific writers
from agents.writers.linkedin_writer import LinkedInWriter
from agents.writers.twitter_writer import TwitterWriter
from agents.writers.instagram_writer import InstagramWriter
from agents.writers.youtube_writer import YouTubeWriter
from agents.writers.newsletter_writer import NewsletterWriter

__all__ = [
    "ControllerAgent",
    "MorningIntakeAgent",
    "TrendAgent",
    "TopicRanker",
    "IdeaGenerator",
    "ResearchAgent",
    "StrategyAgent",
    "ContentAgent",
    "ReviewAgent",
    "PublisherAgent",
    "AnalyticsAgent",
    "MemoryAgent",
    "AutomationAgent",
    "LinkedInWriter",
    "TwitterWriter",
    "InstagramWriter",
    "YouTubeWriter",
    "NewsletterWriter",
]
