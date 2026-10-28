# -*- coding: utf-8 -*-
"""Creator OS API — FastAPI backend for the JAN AI Media Manager dashboard.

Legacy routes are being hardened incrementally before SaaS release. Any route
that accepts tenant data must derive identity from authentication, not a
caller-controlled user_id. Live publishing is disabled through this legacy
endpoint until persisted approval/version records are available.
"""
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import List

from auth.auth_routes import router as auth_router
from auth.auth_routes import get_current_user
from core.saas_security import require_active_user, get_owned_brand
from database.session import get_db
from database.models import User

app = FastAPI(
    title="JAN AI Creator OS",
    description="API for the JAN AI Media Manager — Creator Intelligence Platform",
    version="2.1.0",
)
app.include_router(auth_router)

# Production deployments must define exact frontend origins. Local development
# can use the Vite default plus localhost. Never use wildcard CORS in SaaS.
_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
_allowed_origins = [
    origin.strip()
    for origin in os.getenv("JAN_ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]
if "*" in _allowed_origins:
    raise RuntimeError("JAN_ALLOWED_ORIGINS cannot contain wildcard origins")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

from core.infrastructure import InfrastructureMiddleware, logger
app.add_middleware(InfrastructureMiddleware, max_requests=300, window_seconds=60)

# Keep legacy table initialization for local compatibility only. Production
# should use schema migrations; disabling implicit DDL avoids deploy-time drift.
if os.getenv("JAN_AUTO_CREATE_SCHEMA", "true").lower() == "true":
    try:
        from database.session import engine
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception:
        logger.exception("Failed to initialize database schema")
        if os.getenv("JAN_ENV", "development").lower() == "production":
            raise

BRAND = os.getenv("JAN_BRAND", "janani_ai")

DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
if DASHBOARD_DIR.exists():
    app.mount("/dashboard", StaticFiles(directory=str(DASHBOARD_DIR), html=True), name="dashboard")


@app.get("/")
def root_redirect():
    return RedirectResponse(url="/dashboard/")


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    platform: str = "linkedin"


class DecideRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    agents: List[str] = ["trend", "strategy", "analytics"]


class BrandCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    industry: str = Field(default="", max_length=200)
    tone_profile: str = Field(default="", max_length=4000)
    target_audience: str = Field(default="", max_length=4000)


@app.post("/brands")
def create_brand(
    req: BrandCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    from core.brand_manager import BrandManager
    from core.subscription_manager import SubscriptionManager

    sub_manager = SubscriptionManager(db)
    brand_manager = BrandManager(db)
    current_count = len(brand_manager.get_user_brands(current_user.id))
    if not sub_manager.can_create_brand(current_user.id, current_count):
        raise HTTPException(status_code=403, detail="Brand limit reached for your subscription tier.")

    brand = brand_manager.create_brand(
        current_user.id, req.name, req.industry, req.tone_profile, req.target_audience
    )
    return {"status": "success", "brand_id": brand.id, "name": brand.name}


@app.get("/brands")
def get_brands(
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    from core.brand_manager import BrandManager
    manager = BrandManager(db)
    brands = manager.get_user_brands(current_user.id)
    return {"brands": [{"id": b.id, "name": b.name} for b in brands]}


@app.get("/subscription")
def get_subscription(
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    from core.subscription_manager import SubscriptionManager
    manager = SubscriptionManager(db)
    sub = manager.get_subscription(current_user.id)
    return {
        "tier": sub.plan_tier,
        "posts_used_today": sub.posts_used_today,
        "limits": manager.LIMITS.get(sub.plan_tier, manager.LIMITS["free"]),
    }


@app.get("/status")
def get_status(current_user: User = Depends(require_active_user)):
    """Return current account's engine status (never expose provider secrets)."""
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
        "version": "2.1.0",
    }


class PublishRequest(BaseModel):
    draft_id: str = Field(min_length=1, max_length=200)
    brand_id: int = Field(gt=0)


@app.post("/publish")
def publish_content(
    req: PublishRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """Legacy publish route fails closed until a persisted approval exists.

    The old implementation fabricated a draft from the requested ID and invoked
    live publishing. That behavior is unsafe and falsely implied successful
    publication. Use the approval/versioned publishing-jobs API when implemented.
    """
    get_owned_brand(brand_id=req.brand_id, user=current_user, db=db)
    raise HTTPException(
        status_code=409,
        detail="Legacy publishing is disabled. Create a persisted draft and approve its exact version before publishing.",
    )


@app.get("/assistant/chat")
def get_founder_advice(
    query: str = Field(min_length=1, max_length=4000),
    brand_id: int = 1,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    get_owned_brand(brand_id=brand_id, user=current_user, db=db)
    from agents.founder_agent import FounderAgent
    agent = FounderAgent()
    result = agent.run(query=query, brand_id=brand_id, db=db)
    return {"status": "success", "response": result}


@app.get("/ideas")
def get_idea_feed(
    topic: str = "AI and startups",
    count: int = 3,
    current_user: User = Depends(require_active_user),
):
    if count < 1 or count > 20:
        raise HTTPException(status_code=422, detail="count must be between 1 and 20")
    try:
        from agents.trend_agent import TrendAgent
        from agents.topic_ranker import TopicRanker
        from agents.idea_generator import IdeaGenerator
        trend = TrendAgent(brand=BRAND)
        trend_data = trend.run(query=topic)
        ranker = TopicRanker(brand=BRAND)
        ranked = ranker.run(trends=trend_data.get("trends", []))
        generator = IdeaGenerator(brand=BRAND)
        return generator.run(ranked_topics=ranked.get("ranked_topics", []), count=count)
    except Exception:
        logger.exception("Idea feed generation failed")
        raise HTTPException(status_code=500, detail="Idea generation failed")


@app.get("/trends")
def get_trends(query: str = "AI technology", current_user: User = Depends(require_active_user)):
    try:
        from agents.trend_agent import TrendAgent
        return TrendAgent(brand=BRAND).run(query=query)
    except Exception:
        logger.exception("Trend lookup failed")
        raise HTTPException(status_code=500, detail="Trend lookup failed")


@app.get("/drafts")
def get_drafts(current_user: User = Depends(require_active_user)):
    try:
        from decision_engine.approval_queue import ApprovalQueue
        queue = ApprovalQueue(BRAND)
        return {"drafts": queue.list_drafts(), "brand": BRAND}
    except Exception:
        logger.exception("Draft queue lookup failed")
        raise HTTPException(status_code=500, detail="Draft queue lookup failed")


@app.get("/queue")
def get_approval_queue(current_user: User = Depends(require_active_user)):
    try:
        from decision_engine.approval_queue import ApprovalQueue
        queue = ApprovalQueue(BRAND)
        pending = queue.list_drafts()
        return {"pending_count": len(pending), "items": pending, "brand": BRAND}
    except Exception:
        logger.exception("Approval queue lookup failed")
        raise HTTPException(status_code=500, detail="Approval queue lookup failed")


@app.get("/calendar")
def get_content_calendar(current_user: User = Depends(require_active_user)):
    try:
        from ai_core.performance_learner import get_learned_schedules
        schedules = get_learned_schedules()
    except Exception:
        schedules = {}
    try:
        from decision_engine.approval_queue import ApprovalQueue
        pending = ApprovalQueue(BRAND).list_drafts()
        upcoming = [
            {"topic": d.get("topic", ""), "platform": d.get("platform", ""), "status": "pending"}
            for d in pending[:10]
        ]
    except Exception:
        upcoming = []
    return {"upcoming": upcoming, "optimal_schedules": schedules, "brand": BRAND}


@app.get("/analytics")
def get_analytics(current_user: User = Depends(require_active_user)):
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
    return {"learned_patterns": patterns, "top_performers": top, "brand": BRAND}


@app.post("/generate")
def generate_content(req: GenerateRequest, current_user: User = Depends(require_active_user)):
    writer_map = {
        "linkedin": "agents.writers.linkedin_writer.LinkedInWriter",
        "twitter": "agents.writers.twitter_writer.TwitterWriter",
        "instagram": "agents.writers.instagram_writer.InstagramWriter",
        "youtube": "agents.writers.youtube_writer.YouTubeWriter",
        "newsletter": "agents.writers.newsletter_writer.NewsletterWriter",
    }
    writer_path = writer_map.get(req.platform.lower())
    if not writer_path:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {req.platform}")
    try:
        module_path, class_name = writer_path.rsplit(".", 1)
        import importlib
        writer_class = getattr(importlib.import_module(module_path), class_name)
        result = writer_class(brand=BRAND).run(topic=req.topic)
        from agents.review_agent import ReviewAgent
        review = ReviewAgent(brand=BRAND).run(drafts=result.get("drafts", []))
        return {
            "content": result,
            "review": {
                "pass_rate": review.get("pass_rate"),
                "passed": len(review.get("passed", [])),
                "failed": len(review.get("failed", [])),
            },
        }
    except Exception:
        logger.exception("Content generation failed")
        raise HTTPException(status_code=500, detail="Content generation failed")


@app.post("/decide")
def multi_agent_decide(req: DecideRequest, current_user: User = Depends(require_active_user)):
    try:
        from ai_core.consensus_engine import ConsensusEngine
        return ConsensusEngine(brand=BRAND).decide(question=req.question, agents=req.agents)
    except Exception:
        logger.exception("Decision workflow failed")
        raise HTTPException(status_code=500, detail="Decision workflow failed")


@app.post("/webhook/approve/{draft_id}")
def webhook_approve(draft_id: str, current_user: User = Depends(require_active_user)):
    """Deprecated safe route; use explicit approval API with CSRF protection."""
    raise HTTPException(status_code=410, detail="Legacy approval webhook is disabled; use the versioned approval API.")


@app.post("/webhook/reject/{draft_id}")
def webhook_reject(draft_id: str, current_user: User = Depends(require_active_user)):
    """Deprecated safe route; use explicit rejection API with CSRF protection."""
    raise HTTPException(status_code=410, detail="Legacy rejection webhook is disabled; use the versioned approval API.")


@app.get("/health/live")
def health_live():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    try:
        from database.session import engine
        with engine.connect():
            pass
        return {"status": "ready"}
    except Exception:
        logger.exception("Readiness probe failed")
        raise HTTPException(status_code=503, detail="Dependencies not ready")
