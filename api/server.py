# -*- coding: utf-8 -*-
"""Creator OS API — FastAPI backend for the JAN AI Media Manager dashboard.

Endpoints:
  GET  /ideas          → Idea feed from IdeaGenerator
  GET  /trends         → Trend signals from TrendAgent
  GET  /drafts         → Current drafts in memory
  GET  /queue          → Approval queue
  GET  /calendar       → Content calendar (planned topics)
  GET  /analytics      → Analytics + learning data
  GET  /status         → System status
  POST /generate       → Generate content for a topic
  POST /decide         → Multi-agent consensus on a decision

Run:
  uvicorn api.server:app --reload --port 8000
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional

app = FastAPI(
    title="JAN AI Creator OS",
    description="API for the JAN AI Media Manager — Creator Intelligence Platform",
    version="2.0.0",
)

# Allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BRAND = os.getenv("JAN_BRAND", "janani_ai")


# ── Request Models ─────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    topic: str
    platform: str = "linkedin"

class DecideRequest(BaseModel):
    question: str
    agents: List[str] = ["trend", "strategy", "analytics"]


# ── GET /status ────────────────────────────────────────────────────────────────

@app.get("/status")
def get_status():
    """System status with agent count, LLM provider, cost usage."""
    try:
        from ai_core.llm_router import get_active_provider
        llm = get_active_provider()
    except Exception:
        llm = "unknown"

    try:
        from ai_core.cost_controller import get_controller
        usage = get_controller().usage_dict()
    except Exception:
        usage = {}

    try:
        from agents.agent_registry import registered_names
        agent_count = len(registered_names())
    except Exception:
        agent_count = 0

    try:
        from memory_engine.vector_store import posts_store
        vector_count = posts_store().count()
    except Exception:
        vector_count = 0

    return {
        "brand": BRAND,
        "llm_provider": llm,
        "agents": agent_count,
        "vector_memory": vector_count,
        "cost_usage": usage,
        "version": "2.0.0",
    }


# ── GET /ideas ─────────────────────────────────────────────────────────────────

@app.get("/ideas")
def get_idea_feed(topic: str = "AI and startups", count: int = 3):
    """Generate idea feed from ranked topics."""
    try:
        from agents.trend_agent import TrendAgent
        from agents.topic_ranker import TopicRanker
        from agents.idea_generator import IdeaGenerator

        trend = TrendAgent(brand=BRAND)
        trend_data = trend.run(query=topic)

        ranker = TopicRanker(brand=BRAND)
        ranked = ranker.run(trends=trend_data.get("trends", []))

        generator = IdeaGenerator(brand=BRAND)
        ideas = generator.run(ranked_topics=ranked.get("ranked_topics", []), count=count)

        return ideas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /trends ────────────────────────────────────────────────────────────────

@app.get("/trends")
def get_trends(query: str = "AI technology"):
    """Get current trend signals."""
    try:
        from agents.trend_agent import TrendAgent
        agent = TrendAgent(brand=BRAND)
        return agent.run(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /drafts ────────────────────────────────────────────────────────────────

@app.get("/drafts")
def get_drafts():
    """Get current drafts from approval queue."""
    try:
        from decision_engine.approval_queue import ApprovalQueue
        queue = ApprovalQueue(BRAND)
        return {"drafts": queue.list_pending(), "brand": BRAND}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /queue ─────────────────────────────────────────────────────────────────

@app.get("/queue")
def get_approval_queue():
    """Get approval queue status."""
    try:
        from decision_engine.approval_queue import ApprovalQueue
        queue = ApprovalQueue(BRAND)
        pending = queue.list_pending()
        return {
            "pending_count": len(pending),
            "items": pending,
            "brand": BRAND,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /calendar ──────────────────────────────────────────────────────────────

@app.get("/calendar")
def get_content_calendar():
    """Get planned content from strategy and schedules."""
    try:
        from ai_core.performance_learner import get_learned_schedules
        schedules = get_learned_schedules()
    except Exception:
        schedules = {}

    try:
        from decision_engine.approval_queue import ApprovalQueue
        queue = ApprovalQueue(BRAND)
        pending = queue.list_pending()
        upcoming = [
            {"topic": d.get("topic", ""), "platform": d.get("platform", ""), "status": "pending"}
            for d in pending[:10]
        ]
    except Exception:
        upcoming = []

    return {
        "upcoming": upcoming,
        "optimal_schedules": schedules,
        "brand": BRAND,
    }


# ── GET /analytics ─────────────────────────────────────────────────────────────

@app.get("/analytics")
def get_analytics():
    """Get learning data and analytics."""
    try:
        from ai_core.performance_learner import get_learned_patterns
        patterns = get_learned_patterns()
    except Exception:
        patterns = {}

    try:
        from memory import topic_memory
        top = topic_memory.top_performers(BRAND, limit=5)
    except Exception:
        top = []

    return {
        "learned_patterns": patterns,
        "top_performers": top,
        "brand": BRAND,
    }


# ── POST /generate ─────────────────────────────────────────────────────────────

@app.post("/generate")
def generate_content(req: GenerateRequest):
    """Generate content for a topic on a specific platform."""
    writer_map = {
        "linkedin": "agents.writers.linkedin_writer.LinkedInWriter",
        "twitter": "agents.writers.twitter_writer.TwitterWriter",
        "instagram": "agents.writers.instagram_writer.InstagramWriter",
        "youtube": "agents.writers.youtube_writer.YouTubeWriter",
        "newsletter": "agents.writers.newsletter_writer.NewsletterWriter",
    }
    writer_path = writer_map.get(req.platform)
    if not writer_path:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {req.platform}")

    try:
        module_path, class_name = writer_path.rsplit(".", 1)
        import importlib
        mod = importlib.import_module(module_path)
        WriterClass = getattr(mod, class_name)
        writer = WriterClass(brand=BRAND)
        result = writer.run(topic=req.topic)

        # Auto-review
        from agents.review_agent import ReviewAgent
        reviewer = ReviewAgent(brand=BRAND)
        review = reviewer.run(drafts=result.get("drafts", []))

        return {
            "content": result,
            "review": {
                "pass_rate": review.get("pass_rate"),
                "passed": len(review.get("passed", [])),
                "failed": len(review.get("failed", [])),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /decide ───────────────────────────────────────────────────────────────

@app.post("/decide")
def multi_agent_decide(req: DecideRequest):
    """Run multi-agent consensus on a decision."""
    try:
        from ai_core.consensus_engine import ConsensusEngine
        engine = ConsensusEngine(brand=BRAND)
        result = engine.decide(
            question=req.question,
            agents=req.agents,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
