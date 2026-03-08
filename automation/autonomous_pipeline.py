import logging
from typing import Dict, Any

from core.brand_manager import BrandManager
from decision_engine.approval_queue import get_approval_queue
from agents.trend_agent import TrendAgent
from agents.topic_ranker import TopicRanker
from agents.idea_generator import IdeaGenerator
from agents.strategy_agent import StrategyAgent
from agents.content_agent import ContentAgent
from agents.review_agent import ReviewAgent

logger = logging.getLogger("autonomous_pipeline")

class AutonomousPipeline:
    def __init__(self, db_session):
        self.db = db_session
        self.brand_manager = BrandManager(self.db)
        
    def run_for_brand(self, brand_id: int) -> Dict[str, Any]:
        """
        Executes the fully autonomous content pipeline for a specific brand.
        Observe → Think → Act → Evaluate.
        """
        brand = self.brand_manager.get_brand(brand_id)
        if not brand:
            return {"status": "error", "message": "Brand not found."}
            
        logger.info(f"Starting autonomous pipeline for brand: {brand.name}")
        
        # 1. OBSERVE (Trends)
        trend_agent = TrendAgent(brand=brand.name)
        trend_data = trend_agent.run(query=brand.industry or "Startup")
        trends = trend_data.get("trends", [])
        
        # 2. THINK (Rank and generate ideas)
        ranker = TopicRanker(brand=brand.name)
        ranked = ranker.run(trends=trends)
        top_topic = ranked.get("top_topic", "General Updates")
        
        idea_gen = IdeaGenerator(brand=brand.name)
        ideas = idea_gen.run(topics=[top_topic])
        
        # We need a proper string to pass to strategy
        idea_list = ideas.get("ideas", [])
        top_idea = ""
        if idea_list and isinstance(idea_list[0], dict):
            top_idea = idea_list[0].get("post", "Share an insight.")
        elif idea_list and isinstance(idea_list[0], str):
            top_idea = idea_list[0]
        else:
            top_idea = "General Post"
        
        strategy_agent = StrategyAgent(brand=brand.name)
        strategy = strategy_agent.run(ideas=[top_idea], platform="linkedin")
        
        # 3. ACT (Draft Content)
        content_agent = ContentAgent(brand=brand.name)
        # Assuming strategy.get returns dict with keys, we wrap in list if needed
        drafts = content_agent.run(strategy=[strategy.get("strategy", {})], platform="linkedin")
        created_drafts = drafts.get("drafts", [])
        
        if not created_drafts:
            logger.warning("Pipeline found no drafts generated.")
            return {"status": "completed", "drafts": 0}
            
        draft_content = created_drafts[0]
        if isinstance(draft_content, str):
            draft_content = {"draft": draft_content}
            
        # 4. EVALUATE (Review)
        reviewer = ReviewAgent(brand=brand.name)
        review_result = reviewer.run(drafts=[draft_content])
        
        # Publish or Queue
        if review_result.get("passed", False) or review_result.get("status") == "passed":
            # Pass brand_id and platform along with draft content to queue
            draft_content["brand_id"] = brand_id
            draft_content["platform"] = "linkedin"  # Defaulting for now
            get_approval_queue().add_draft(draft_content)
            logger.info(f"Pipeline finished. Draft added to queue for {brand.name}")
            return {"status": "success", "message": "Draft queued for approval.", "draft": draft_content}
        else:
            logger.warning("Pipeline draft failed quality review.")
            return {"status": "failed_review", "review": review_result}
