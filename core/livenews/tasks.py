from celery import shared_task
from .services import GuardianNewsService

@shared_task
def refresh_news():
    """Celery task to refresh news from The Guardian API."""
    service = GuardianNewsService()
    service.refresh_news() 