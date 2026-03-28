from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ContentRequest(BaseModel):
    topic: str
    tone: str = "professional"
    platform: str = "linkedin"

class ContentResponse(BaseModel):
    content: str

class PostCreate(BaseModel):
    topic: str
    content: str
    platform: str

class PostResponse(BaseModel):
    id: int
    topic: str
    content: str
    platform: str
    created_at: datetime
    class Config:
        from_attributes = True

class ScheduleRequest(BaseModel):
    post_id: int
    run_at: datetime
