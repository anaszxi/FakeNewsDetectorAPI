from django.core.management.base import BaseCommand
from core.livenews.services import GuardianNewsService
from core.livenews.models import NewsCategory
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test Guardian API integration'

    def handle(self, *args, **kwargs):
        service = GuardianNewsService()
        
        # Create or get the World category
        category, _ = NewsCategory.objects.get_or_create(
            name='world',
            defaults={'is_active': True}
        )
        
        self.stdout.write(f"\nTesting category: {category.name}")
        self.stdout.write("-" * 80)
        
        # Fetch news
        self.stdout.write("Fetching news...")
        news_items = service.fetch_news(category)
        
        if news_items:
            self.stdout.write(f"Found {len(news_items)} articles")
            self.stdout.write("\nFirst article:")
            article = news_items[0]
            self.stdout.write(f"Title: {article.get('webTitle')}")
            self.stdout.write(f"URL: {article.get('webUrl')}")
            self.stdout.write(f"Fields: {list(article.get('fields', {}).keys())}")
            
            # Process news
            self.stdout.write("\nProcessing articles...")
            processed = service.process_news(news_items, category)
            self.stdout.write(self.style.SUCCESS(f"Successfully processed {processed} articles"))
        else:
            self.stdout.write(self.style.ERROR("No articles found"))
        
        self.stdout.write("-" * 80) 