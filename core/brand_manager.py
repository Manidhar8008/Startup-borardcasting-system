from sqlalchemy.orm import Session
from database.models import Brand, User
from typing import Optional, Dict, List

class BrandManager:
    def __init__(self, db: Session):
        self.db = db
        
    def get_brand(self, brand_id: int) -> Optional[Brand]:
        return self.db.query(Brand).filter(Brand.id == brand_id).first()
        
    def get_user_brands(self, user_id: int) -> List[Brand]:
        return self.db.query(Brand).filter(Brand.owner_id == user_id).all()
        
    def create_brand(self, user_id: int, name: str, industry: str = "", tone_profile: str = "", target_audience: str = "") -> Brand:
        # Check if user is allowed to create more brands (Subscription check happens via SubscriptionManager)
        brand = Brand(
            owner_id=user_id,
            name=name,
            industry=industry,
            tone_profile=tone_profile,
            target_audience=target_audience
        )
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand
        
    def get_brand_context(self, brand_id: int) -> Dict:
        brand = self.get_brand(brand_id)
        if not brand:
            return {}
            
        return {
            "name": brand.name,
            "industry": brand.industry,
            "tone_profile": brand.tone_profile,
            "target_audience": brand.target_audience
        }
