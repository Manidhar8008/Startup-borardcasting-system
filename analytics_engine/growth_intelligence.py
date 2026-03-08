import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database.models import Analytics, Content

logger = logging.getLogger("growth_intelligence")

class GrowthIntelligence:
    def __init__(self, db: Session):
        self.db = db
        
    def get_brand_performance(self, brand_id: int, days: int = 30) -> dict:
        """Calculate overall brand performance over a time window."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Aggregate analytics
        stats = self.db.query(
            func.sum(Analytics.views).label("total_views"),
            func.sum(Analytics.likes).label("total_likes"),
            func.sum(Analytics.comments).label("total_comments"),
            func.sum(Analytics.shares).label("total_shares")
        ).join(
            Content, Content.id == Analytics.content_id
        ).filter(
            Content.brand_id == brand_id,
            Analytics.last_updated >= cutoff_date
        ).first()
        
        if not stats or not stats.total_views:
            return {
                "period_days": days,
                "metrics": {"views": 0, "likes": 0, "comments": 0, "shares": 0},
                "best_format": "unknown",
                "recommendation": "Not enough data yet. Establish a posting rhythm to gather insights."
            }
        
        # Find best performing post type
        best_post = self.db.query(Content, Analytics).join(
            Analytics, Content.id == Analytics.content_id
        ).filter(
            Content.brand_id == brand_id,
            Analytics.last_updated >= cutoff_date
        ).order_by(Analytics.likes.desc()).first()
        
        best_format = best_post.Content.platform if best_post else "unknown"
        
        return {
            "period_days": days,
            "metrics": {
                "views": stats.total_views or 0,
                "likes": stats.total_likes or 0,
                "comments": stats.total_comments or 0,
                "shares": stats.total_shares or 0
            },
            "best_format": best_format,
            "recommendation": f"Double down on {best_format} formats based on recent high engagement."
        }
