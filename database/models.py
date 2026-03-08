from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    brands = relationship("Brand", back_populates="owner")
    subscription = relationship("Subscription", back_populates="user", uselist=False)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_tier = Column(String, default="free") # free, pro, agency
    posts_used_today = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="subscription")

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    industry = Column(String)
    tone_profile = Column(Text)
    target_audience = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="brands")
    content = relationship("Content", back_populates="brand")

class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    topic = Column(String)
    platform = Column(String)  # linkedin, twitter, etc.
    status = Column(String, default="draft") # draft, pending, approved, published, rejected
    draft_text = Column(Text)
    published_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    brand = relationship("Brand", back_populates="content")
    analytics = relationship("Analytics", back_populates="content", uselist=False)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"))
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    content = relationship("Content", back_populates="analytics")
