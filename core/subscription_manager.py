from sqlalchemy.orm import Session
from database.models import Subscription, User
from datetime import datetime, timedelta

class SubscriptionManager:
    LIMITS = {
        "free": {"max_brands": 1, "max_posts_per_day": 5},
        "pro": {"max_brands": 3, "max_posts_per_day": 999999}, # effectively unlimited
        "agency": {"max_brands": 100, "max_posts_per_day": 999999}
    }

    def __init__(self, db: Session):
        self.db = db
        
    def get_subscription(self, user_id: int) -> Subscription:
        sub = self.db.query(Subscription).filter(Subscription.user_id == user_id).first()
        if not sub:
            sub = Subscription(user_id=user_id, plan_tier="free")
            self.db.add(sub)
            self.db.commit()
            self.db.refresh(sub)
        return sub
        
    def check_post_quota(self, user_id: int) -> bool:
        sub = self.get_subscription(user_id)
        
        # Reset quota if it's a new day
        if sub.last_reset_date.date() < datetime.utcnow().date():
            sub.posts_used_today = 0
            sub.last_reset_date = datetime.utcnow()
            self.db.commit()
            
        limit = self.LIMITS.get(sub.plan_tier, self.LIMITS["free"])["max_posts_per_day"]
        
        return sub.posts_used_today < limit
        
    def record_post_usage(self, user_id: int):
        sub = self.get_subscription(user_id)
        sub.posts_used_today += 1
        self.db.commit()
        
    def can_create_brand(self, user_id: int, current_brand_count: int) -> bool:
        sub = self.get_subscription(user_id)
        limit = self.LIMITS.get(sub.plan_tier, self.LIMITS["free"])["max_brands"]
        return current_brand_count < limit
