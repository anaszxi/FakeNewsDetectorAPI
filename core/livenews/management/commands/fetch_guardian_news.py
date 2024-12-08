from django.core.management.base import BaseCommand
from django.db import transaction
from core.livenews.services import GuardianNewsService
from core.livenews.models import NewsCategory
import logging
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch news from The Guardian API'

    def handle(self, *args, **kwargs):
        service = GuardianNewsService()
        
        self.stdout.write('Starting news fetch from The Guardian...')
        
        # Get active categories
        categories = NewsCategory.objects.filter(is_active=True)
        self.stdout.write(f'Found {categories.count()} active categories')
        
        # Process each category in a separate transaction
        for category in categories:
            try:
                with transaction.atomic():
                    self.stdout.write(f'Fetching news for category: {category.name}')
                    news_items = service.fetch_news(category)
                    if news_items:
                        processed = service.process_news(news_items, category)
                        self.stdout.write(f'Processed {processed} news items for {category.name}')
                    else:
                        self.stdout.write(f'No news items found for {category.name}')
                    
                    # Update last fetch time
                    category.update_last_fetch()
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing category {category.name}: {str(e)}'))
                continue
                
            # Small delay between categories to avoid overwhelming the API
            time.sleep(1)
        
        self.stdout.write(self.style.SUCCESS('Successfully fetched news from The Guardian')) 