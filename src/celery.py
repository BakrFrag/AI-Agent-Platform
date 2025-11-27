# app/celery_app.py

from celery import Celery
from src.core import settings
celery_app = Celery(
    "audio_worker",
    broker= settings.CELERY_BROKER_URL,
    backend= settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        # optional routing
    }
)
