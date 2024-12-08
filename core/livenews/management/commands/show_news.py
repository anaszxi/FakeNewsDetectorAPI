from django.core.management.base import BaseCommand
from core.livenews.models import LiveNews, NewsCategory
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Show current news in the database'

    def handle(self, *args, **kwargs):
        # Show active categories
        categories = NewsCategory.objects.filter(is_active=True)
        self.stdout.write("\nActive Categories:")
        for cat in categories:
            last_fetch = cat.last_fetch
            if last_fetch:
                age = timezone.now() - last_fetch
                age_str = f"{age.seconds // 60} minutes ago"
            else:
                age_str = "never"
                
            self.stdout.write(f"- {cat.name} (Last fetch: {age_str})")
        
        # Show recent news
        recent = timezone.now() - timedelta(hours=24)
        news = LiveNews.objects.filter(publication_date__gte=recent).order_by('-publication_date')
        
        self.stdout.write(f"\nRecent News (last 24 hours): {news.count()} articles")
        for article in news[:10]:  # Show first 10
            self.stdout.write(f"\nTitle: {article.title[:100]}...")
            self.stdout.write(f"Category: {article.news_category}")
            self.stdout.write(f"Published: {article.publication_date}")
            self.stdout.write(f"Reliability Score: {article.reliability_score}%")
            
        # Show statistics
        total = LiveNews.objects.count()
        reliable = LiveNews.objects.filter(prediction=True).count()
        unreliable = total - reliable
        
        self.stdout.write(f"\nStatistics:")
        self.stdout.write(f"Total articles: {total}")
        self.stdout.write(f"Reliable: {reliable} ({(reliable/total*100 if total else 0):.1f}%)")
        self.stdout.write(f"Unreliable: {unreliable} ({(unreliable/total*100 if total else 0):.1f}%)") 