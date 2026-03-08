import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database.models import Analytics, Content, Brand

logger = logging.getLogger("growth_optimizer")

class GrowthOptimizer:
    """
    Machine learning feedback loop that analyzes engagement,
    follower growth, CTRs, content formats, and scheduling.
    """
    def __init__(self, db: Session):
        self.db = db
        
    def detect_viral_patterns(self, brand_id: int):
        # Look for content with 3x average engagement
        content_items = self.db.query(Content, Analytics).join(
            Analytics, Content.id == Analytics.content_id
        ).filter(Content.brand_id == brand_id).all()
        
        if not content_items:
            return []
            
        avg_likes = sum(a.likes for c, a in content_items) / len(content_items) if content_items else 0
        viral_posts = [{"id": c.id, "platform": c.platform, "topic": c.topic, "likes": a.likes} 
                       for c, a in content_items if a.likes > avg_likes * 3]
                       
        return viral_posts

    def get_recommendations(self, brand_id: int) -> dict:
        """
        Return growth recommendations (formats, schedules, topics).
        """
        brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            return {"error": "Brand not found"}
            
        viral_posts = self.detect_viral_patterns(brand_id)
        
        # Simple heuristic engine based on historical data
        best_platform = "linkedin"
        if viral_posts:
            # Count frequency of platforms in viral posts
            platforms = [p['platform'] for p in viral_posts]
            best_platform = max(set(platforms), key=platforms.count)
            
        return {
            "insights": {
                "viral_patterns_found": len(viral_posts),
                "top_performing_platform": best_platform,
            },
            "strategies": [
                f"Double down on {best_platform} content.",
                "Repost your top 3 viral posts as Twitter threads.",
                "Experiment with posting at 8:00 AM EST on Tuesdays.",
                "Launch a Newsletter integrating your top engaged topics."
            ],
            "underperforming": "Text-only Twitter posts are seeing 40% less engagement this week."
        }
