from django.core.management.base import BaseCommand
from core.livenews.models import LiveNews, NewsCategory

class Command(BaseCommand):
    help = 'Reset news database by clearing all articles and deactivating categories'

    def handle(self, *args, **kwargs):
        # Delete all news articles
        news_count = LiveNews.objects.count()
        LiveNews.objects.all().delete()
        self.stdout.write(f"Deleted {news_count} news articles")
        
        # Deactivate all categories except main ones
        main_categories = ['world', 'politics', 'technology', 'science', 'business']
        
        # Deactivate all categories first
        NewsCategory.objects.all().update(is_active=False)
        
        # Activate only main categories
        for category in main_categories:
            NewsCategory.objects.update_or_create(
                name=category,
                defaults={'is_active': True}
            )
            
        self.stdout.write(f"Reset categories to {', '.join(main_categories)}")
        self.stdout.write(self.style.SUCCESS("Successfully reset news database")) 