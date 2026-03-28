from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from backend.db.database import engine, Base, get_db
from backend.models import models, schemas
from backend.services.generator import generate_post
from backend.tasks import execute_post_task
from automation.playwright_scripts.poster import auto_post_content
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import datetime
import os

# Create DB Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jan.ai MVP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Celery operates out of band, no in-memory polling loops required.
    pass

@app.post("/generate-content", response_model=schemas.ContentResponse)
def api_generate_content(req: schemas.ContentRequest):
    content = generate_post(req.topic, req.tone, req.platform)
    return {"content": content}

@app.post("/posts", response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    db_post = models.Post(topic=post.topic, content=post.content, platform=post.platform)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Memory logger
    db.add(models.Log(post_id=db_post.id, action="created_post", platform=post.platform, status="success"))
    db.commit()
    return db_post

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()

@app.post("/schedule-post")
def api_schedule_post(req: schemas.ScheduleRequest, db: Session = Depends(get_db)):
    # 1. Reject past timestamps
    if req.run_at.replace(tzinfo=None) < datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="run_at cannot be in the past.")

    post = db.query(models.Post).filter(models.Post.id == req.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Task State System: PENDING
    task = models.Task(post_id=req.post_id, run_at=req.run_at, status=models.TaskState.PENDING.value)
    db.add(task)
    db.commit()
    db.refresh(task)

    # Queue to Celery
    execute_post_task.apply_async(args=[task.id], eta=req.run_at)
    return {"status": "Task Queued in Celery", "task_id": task.id, "run_at": req.run_at}

@app.post("/auto-post")
def api_auto_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    task = models.Task(post_id=post.id, run_at=datetime.datetime.utcnow(), status=models.TaskState.PENDING.value)
    db.add(task)
    db.commit()
    db.refresh(task)

    # Trigger immediately
    execute_post_task.delay(task.id)
    return {"status": "Task Executing Async via Celery", "task_id": task.id}

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    try:
        html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Jan.ai API Running. Go to /docs</h1><p>{str(e)}</p>"
