from django.core.management.base import BaseCommand
from django.utils import timezone
from core.livenews.models import LiveNews

class Command(BaseCommand):
    help = 'Loads sample news data with prediction field testing'

    def handle(self, *args, **kwargs):
        # Sample news data with prediction field testing
        news_data = [
            {
                'title': 'Major Political Reform Announced by Government',
                'news_category': 'News',
                'section_id': 'politics',
                'section_name': 'Politics',
                'type': 'article',
                'web_url': 'https://example.com/politics/reform',
                'img_url': 'https://example.com/images/reform.jpg',
                'prediction': True  # Real news
            },
            {
                'title': 'Aliens Found Living Among Us, Claims Anonymous Source',
                'news_category': 'News',
                'section_id': 'conspiracy',
                'section_name': 'Conspiracy',
                'type': 'article',
                'web_url': 'https://example.com/conspiracy/aliens',
                'img_url': 'https://example.com/images/aliens.jpg',
                'prediction': False  # Fake news
            },
            {
                'title': 'Champions League Final Results: Real Madrid Wins',
                'news_category': 'Sport',
                'section_id': 'football',
                'section_name': 'Football',
                'type': 'article',
                'web_url': 'https://example.com/sport/champions-league',
                'img_url': 'https://example.com/images/football.jpg',
                'prediction': True  # Real news
            },
            {
                'title': 'Player Scores 1000 Goals in Single Match, Claims Coach',
                'news_category': 'Sport',
                'section_id': 'football',
                'section_name': 'Football',
                'type': 'article',
                'web_url': 'https://example.com/sport/impossible-goals',
                'img_url': 'https://example.com/images/goals.jpg',
                'prediction': False  # Fake news
            },
            {
                'title': 'New Art Exhibition Opens at National Gallery',
                'news_category': 'Arts',
                'section_id': 'culture',
                'section_name': 'Culture',
                'type': 'article',
                'web_url': 'https://example.com/arts/exhibition',
                'img_url': 'https://example.com/images/exhibition.jpg',
                'prediction': True  # Real news
            },
            {
                'title': 'Artist Claims to Paint Using Thoughts Alone',
                'news_category': 'Arts',
                'section_id': 'culture',
                'section_name': 'Culture',
                'type': 'article',
                'web_url': 'https://example.com/arts/thought-painting',
                'img_url': 'https://example.com/images/painting.jpg',
                'prediction': False  # Fake news
            },
            {
                'title': 'New Study Shows Benefits of Regular Exercise',
                'news_category': 'Lifestyle',
                'section_id': 'health',
                'section_name': 'Health',
                'type': 'article',
                'web_url': 'https://example.com/lifestyle/exercise',
                'img_url': 'https://example.com/images/exercise.jpg',
                'prediction': True  # Real news
            },
            {
                'title': 'Miracle Diet: Lose 50 Pounds in 5 Days',
                'news_category': 'Lifestyle',
                'section_id': 'health',
                'section_name': 'Health',
                'type': 'article',
                'web_url': 'https://example.com/lifestyle/miracle-diet',
                'img_url': 'https://example.com/images/diet.jpg',
                'prediction': False  # Fake news
            }
        ]

        count = 0
        for data in news_data:
            _, created = LiveNews.objects.get_or_create(
                title=data['title'],
                defaults={
                    'publication_date': timezone.now(),
                    'news_category': data['news_category'],
                    'prediction': data['prediction'],
                    'section_id': data['section_id'],
                    'section_name': data['section_name'],
                    'type': data['type'],
                    'web_url': data['web_url'],
                    'img_url': data['img_url']
                }
            )
            if created:
                count += 1
                self.stdout.write(f"Created news article: {data['title']} (Prediction: {'Real' if data['prediction'] else 'Fake'})")

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} news articles')) 