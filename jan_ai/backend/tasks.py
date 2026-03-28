from backend.celery_app import celery_app
from backend.db.database import SessionLocal
from backend.models.models import Task, TaskState, TaskLog
from automation.playwright_scripts.poster import auto_post_content
import datetime
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, time_limit=300)
def execute_post_task(self, task_id: int):
    """
    Celery worker resolving the State System, Priority, and Timeout handling.
    Executes a Post against the Hybrid pipeline.
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found in Database.")
            return

        # Prevent double-run safety lock
        if task.status in [TaskState.SUCCESS.value, TaskState.RUNNING.value]:
            logger.warning(f"Task {task_id} already in states {task.status}. Aborting redundant execute.")
            return

        # Advance to RUNNING State
        task.status = TaskState.RUNNING.value
        db.add(TaskLog(task_id=task.id, step_name="Initialization", status="SUCCESS", message="Celery worker claimed task"))
        db.commit()

        logger.info(f"Executing post ID {task.post_id} on {task.post.platform}...")
        
        # Step log
        db.add(TaskLog(task_id=task.id, step_name="Execution_Start", status="RUNNING", message="Triggering Hybrid Poster logic"))
        db.commit()
        
        success = auto_post_content(task.post.platform, task.post.topic, task.post.content)
        
        if success:
            task.status = TaskState.SUCCESS.value
            db.add(TaskLog(task_id=task.id, step_name="Completion", status="SUCCESS", message="Playwright automation succeeded natively"))
        else:
            raise Exception("Hybrid Automation script returned False. Triggering localized failure.")
            
        db.commit()

    except Exception as exc:
        task.retry_count += 1
        db.add(TaskLog(task_id=task.id, step_name="Execution_Failure", status="FAILED", message=str(exc)))
        
        if task.retry_count >= task.max_retries:
            task.status = TaskState.FAILED.value
            task.error_message = f"Max Retries Reached (3/3): {str(exc)}"
            db.commit()
            logger.critical(f"Task {task_id} completely failed after 3 heavy retries.")
        else:
            task.status = TaskState.RETRY.value
            db.commit()
            logger.warning(f"Task {task_id} failed logic branch. Retrying safely in 5 minutes via Celery backoff...")
            self.retry(exc=exc, countdown=300)

    finally:
        db.close()
