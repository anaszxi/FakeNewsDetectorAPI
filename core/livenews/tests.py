from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient
from .models import LiveNews
import datetime

class LiveNewsModelTests(TestCase):
    def setUp(self):
        self.valid_news = {
            'title': 'Test News Article Title',
            'publication_date': timezone.now(),
            'news_category': 'Politics',
            'prediction': True,
            'section_id': 'politics',
            'section_name': 'Politics',
            'type': 'article',
            'web_url': 'https://example.com/news',
            'img_url': 'https://example.com/image.jpg'
        }

    def test_create_valid_news(self):
        news = LiveNews.objects.create(**self.valid_news)
        self.assertEqual(news.title, self.valid_news['title'])
        self.assertEqual(news.type, 'article')

    def test_title_min_length(self):
        self.valid_news['title'] = 'Short'  # Less than 10 characters
        with self.assertRaises(ValidationError):
            news = LiveNews.objects.create(**self.valid_news)
            news.full_clean()

    def test_invalid_url(self):
        self.valid_news['web_url'] = 'invalid-url'
        with self.assertRaises(ValidationError):
            news = LiveNews.objects.create(**self.valid_news)
            news.full_clean()

    def test_invalid_type_choice(self):
        self.valid_news['type'] = 'invalid_type'
        with self.assertRaises(ValidationError):
            news = LiveNews.objects.create(**self.valid_news)
            news.full_clean()

    def test_str_representation(self):
        news = LiveNews.objects.create(**self.valid_news)
        self.assertEqual(str(news), self.valid_news['title'])

    def test_ordering(self):
        older_news = LiveNews.objects.create(
            title="Older News Article Title",
            publication_date=timezone.now() - datetime.timedelta(days=1),
            news_category="Politics",
            prediction=True,
            section_id="politics",
            section_name="Politics",
            type="article",
            web_url="https://example.com/old-news",
            img_url="https://example.com/old-image.jpg"
        )
        newer_news = LiveNews.objects.create(**self.valid_news)
        
        news_list = LiveNews.objects.all()
        self.assertEqual(news_list[0], newer_news)
        self.assertEqual(news_list[1], older_news)

class LiveNewsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.news = LiveNews.objects.create(
            title="Test News Article",
            publication_date=timezone.now(),
            news_category="Test",
            prediction=True,
            section_id="test-section",
            section_name="Test Section",
            type="article",
            web_url="https://test.com",
            img_url="https://test.com/image.jpg"
        )

    def test_get_news_list(self):
        response = self.client.get('/api/v1/news/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test News Article")

    def test_get_news_by_category(self):
        response = self.client.get('/api/v1/news/category/Test/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['news_category'], 'Test')

    def test_get_news_detail(self):
        response = self.client.get(f'/api/v1/news/{self.news.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test News Article')

    def test_get_nonexistent_news(self):
        response = self.client.get('/api/v1/news/999/')
        self.assertEqual(response.status_code, 404)

    def test_get_news_by_invalid_category(self):
        response = self.client.get('/api/v1/news/category/NonExistent/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_news_ordering(self):
        older_news = LiveNews.objects.create(
            title="Older News Article",
            publication_date=timezone.now() - datetime.timedelta(days=1),
            news_category="Test",
            prediction=True,
            section_id="test-section",
            section_name="Test Section",
            type="article",
            web_url="https://test.com/older",
            img_url="https://test.com/older-image.jpg"
        )
        
        response = self.client.get('/api/v1/news/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['title'], "Test News Article")

    def test_news_prediction_field(self):
        fake_news = LiveNews.objects.create(
            title="Fake News Article Test",
            publication_date=timezone.now(),
            news_category="Test",
            prediction=False,
            section_id="test-section",
            section_name="Test Section",
            type="article",
            web_url="https://test.com/fake",
            img_url="https://test.com/fake-image.jpg"
        )
        
        response = self.client.get(f'/api/v1/news/{fake_news.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['prediction'])

    def test_multiple_categories(self):
        LiveNews.objects.create(
            title="Politics News Article",
            publication_date=timezone.now(),
            news_category="Politics",
            prediction=True,
            section_id="politics",
            section_name="Politics",
            type="article",
            web_url="https://test.com/politics",
            img_url="https://test.com/politics-image.jpg"
        )
        
        # Test Politics category
        response = self.client.get('/api/v1/news/category/Politics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['news_category'], 'Politics')
        
        # Test Test category
        response = self.client.get('/api/v1/news/category/Test/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['news_category'], 'Test')
