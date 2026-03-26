import os

from celery import Celery

# Read Redis URL from env
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

# Result backend uses DB 1
RESULT_BACKEND = REDIS_URL.replace("/0", "/1") if "/0" in REDIS_URL else REDIS_URL + "/1"

celery_app = Celery(
    "facebook_auto_poster",
    broker=REDIS_URL,
    backend=RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_time_limit=300,
    task_soft_time_limit=250,
    task_track_started=True,
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.tasks"])

# Beat schedule
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "check-publish-slots": {
        "task": "app.tasks.publish_task.check_publish_slots",
        "schedule": 60.0,
        "options": {"expires": 55},
    },
    "update-heartbeat": {
        "task": "app.tasks.health_task.update_heartbeat",
        "schedule": 60.0,
    },
    "check-token-health": {
        "task": "app.tasks.health_task.check_all_tokens",
        "schedule": crontab(hour=3, minute=0),
    },
    "daily-report": {
        "task": "app.tasks.report_task.send_daily_report",
        "schedule": crontab(hour=8, minute=0),
    },
}
