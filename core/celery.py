import os
from celery import Celery
from django.core import settings
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Use settings from Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'refresh-news-every-10-minutes': {
        'task': 'core.livenews.tasks.refresh_news',
        'schedule': crontab(minute='*/10'),  # Run every 10 minutes
    },
} 