"""
Celery application configuration.
"""
from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "leadgen",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Optional: Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-data": {
        "task": "app.workers.tasks.cleanup_old_data",
        "schedule": 86400.0,  # Daily
    },
}
