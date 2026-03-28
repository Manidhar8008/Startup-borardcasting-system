from apscheduler.schedulers.background import BackgroundScheduler
from backend.db.database import SessionLocal
from backend.models.models import Schedule, Post, Log
from automation.playwright_scripts.poster import auto_post_content
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
scheduler = BackgroundScheduler()

def check_scheduled_posts():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        due_jobs = db.query(Schedule).filter(Schedule.status == "pending", Schedule.run_at <= now).all()
        for job in due_jobs:
            post = db.query(Post).filter(Post.id == job.post_id).first()
            if post:
                logging.info(f"Executing scheduled post ID {post.id} for {post.platform}")
                success = auto_post_content(post.platform, post.topic, post.content)
                
                if success:
                    job.status = "published"
                else:
                    import datetime as dt
                    logging.warning(f"Post {post.id} failed automation, scheduling a retry in 5 minutes.")
                    job.run_at = job.run_at + dt.timedelta(minutes=5)
                    job.status = "pending"
                
                # Log Memory
                log_entry = Log(post_id=post.id, action="scheduled_auto_post", platform=post.platform, status=job.status)
                db.add(log_entry)
            else:
                job.status = "failed"
            db.commit()
    finally:
        db.close()

def init_scheduler():
    scheduler.add_job(check_scheduled_posts, 'interval', minutes=1)
    if not scheduler.running:
        scheduler.start()
