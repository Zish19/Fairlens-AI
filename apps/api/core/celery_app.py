import os
from celery import Celery
from apps.api.core.config import settings

# Initialize Celery
celery_app = Celery(
    "fairlens",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["apps.api.tasks.analysis_tasks", "apps.api.tasks.upload_tasks"]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    task_reject_on_worker_lost=True,
)
