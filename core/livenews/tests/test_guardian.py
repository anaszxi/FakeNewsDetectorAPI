from django.test import TestCase
from core.livenews.services import GuardianNewsService
from core.livenews.models import NewsCategory

class GuardianAPITest(TestCase):
    def setUp(self):
        self.service = GuardianNewsService()
        self.category = NewsCategory.objects.create(
            name='world',
            is_active=True
        )

    def test_fetch_news(self):
        """Test fetching news from Guardian API."""
        print("\nTesting Guardian API news fetching...")
        
        # Fetch news
        news_items = self.service.fetch_news(self.category)
        self.assertIsNotNone(news_items, "News items should not be None")
        self.assertTrue(len(news_items) > 0, "Should find at least one news item")
        
        if news_items:
            article = news_items[0]
            print(f"\nFirst article:")
            print(f"Title: {article.get('webTitle')}")
            print(f"URL: {article.get('webUrl')}")
            print(f"Fields: {list(article.get('fields', {}).keys())}")
            
            # Test processing
            processed = self.service.process_news(news_items, self.category)
            self.assertTrue(processed > 0, "Should process at least one article")
            print(f"\nProcessed {processed} articles") 