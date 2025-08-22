from celery import Celery
from datetime import timezone


celery_app = Celery(
    "worker", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)
celery_app.timezone = timezone.utc
