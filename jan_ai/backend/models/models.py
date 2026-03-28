from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.db.database import Base
import datetime
import enum

class TaskMode(str, enum.Enum):
    NORMAL = "NORMAL"
    SAFE_MODE = "SAFE_MODE" # Freezes outbound mutations

class TaskPriority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TaskState(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRY = "RETRY"

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_type = Column(String)
    audience = Column(String)
    tone = Column(String)
    platforms = Column(String) # CSV or JSON
    posting_frequency = Column(String)
    enable_auto_post = Column(Boolean, default=True)
    reddit_enabled = Column(Boolean, default=True)
    twitter_enabled = Column(Boolean, default=False)
    linkedin_enabled = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    topic = Column(String)
    content = Column(Text)
    platform = Column(String) # linkedin, twitter, reddit
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    priority = Column(String, default=TaskPriority.MEDIUM.value)
    status = Column(String, default=TaskState.PENDING.value)
    run_at = Column(DateTime)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    post = relationship("Post")

class TaskLog(Base):
    __tablename__ = "task_logs"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    step_name = Column(String)
    status = Column(String)  # RUNNING/SUCCESS/FAILED
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
