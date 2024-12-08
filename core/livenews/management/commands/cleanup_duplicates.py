from django.core.management.base import BaseCommand
from django.db.models import Count
from core.livenews.models import LiveNews
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up duplicate news entries based on web_url'

    def handle(self, *args, **kwargs):
        # Find duplicates
        duplicates = (
            LiveNews.objects.values('web_url')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        
        self.stdout.write(f"Found {len(duplicates)} URLs with duplicates")
        
        # Process each duplicate group
        for dup in duplicates:
            url = dup['web_url']
            entries = LiveNews.objects.filter(web_url=url).order_by('-publication_date')
            
            # Keep the most recent entry
            keep = entries.first()
            to_delete = entries.exclude(id=keep.id)
            
            self.stdout.write(f"URL: {url}")
            self.stdout.write(f"- Keeping: {keep.title[:50]}...")
            self.stdout.write(f"- Deleting {to_delete.count()} duplicates")
            
            # Delete duplicates
            to_delete.delete()
        
        self.stdout.write(self.style.SUCCESS("Successfully cleaned up duplicate entries")) 