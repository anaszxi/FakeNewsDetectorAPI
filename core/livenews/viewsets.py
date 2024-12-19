from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import LiveNews, NewsCategory
from .serializers import LiveNewsSerializer, LiveNewsDetailedSerializer, NewsSerializer, CategorySerializer
from .services import GuardianNewsService, fake_news_service
from core.model import load_models
import logging
import threading
import time
import requests
from bs4 import BeautifulSoup
from django.db import models
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)

class RateLimitMixin:
    _last_request_time = {}
    _request_interval = 1.0  # 1 second between requests

    def _wait_for_rate_limit(self):
        current_time = time.time()
        if self.__class__ in self._last_request_time:
            time_since_last_request = current_time - self._last_request_time[self.__class__]
            if time_since_last_request < self._request_interval:
                time.sleep(self._request_interval - time_since_last_request)
        self._last_request_time[self.__class__] = time.time()

def get_new_news_from_api_and_update():
    """Gets news from the guardian news using it's API"""
    try:
        # Use the GuardianNewsService to handle API calls with rate limiting and proper SSL verification
        service = GuardianNewsService()
        news_data = service.get_news_from_api()  # Remove verify parameter as it's handled in the service
        
        if not news_data or "response" not in news_data or "results" not in news_data["response"]:
            logger.error("Invalid response format from Guardian API")
            return

        for article in news_data["response"]["results"]:
            try:
                title = article.get("webTitle")
                publication_date_str = article.get("webPublicationDate")
                category = article.get("pillarName", "Undefined")
                section_id = article.get("sectionId")
                section_name = article.get("sectionName")
                article_type = article.get("type")
                web_url = article.get("webUrl")

                if not title or not publication_date_str:
                    continue

                # Convert string to datetime with timezone
                try:
                    publication_date = datetime.strptime(publication_date_str, '%Y-%m-%dT%H:%M:%SZ')
                    publication_date = timezone.make_aware(publication_date)
                except ValueError:
                    logger.error(f"Invalid date format: {publication_date_str}")
                    continue

                # Create or update the news entry
                LiveNews.objects.update_or_create(
                    web_url=web_url,  # Use web_url as the unique identifier
                    defaults={
                        'title': title,
                        'publication_date': publication_date,
                        'news_category': category,
                        'section_id': section_id,
                        'section_name': section_name,
                        'type': article_type
                    }
                )

            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Unexpected error in get_new_news_from_api_and_update: {str(e)}")

def scrap_img_from_web(url):
    """Scrape image from article webpage."""
    try:
        r = requests.get(url, verify=True)
        if r.status_code != 200:
            return "None"
        web_content = r.content
        soup = BeautifulSoup(web_content, 'html.parser')
        try:
            imgs = soup.find_all('article')[0].find_all('img', class_='dcr-evn1e9')
            img_urls = []
            for img in imgs:
                src = img.get("src")
                img_urls.append(src)
        
            if not img_urls:
                return "None"
            return img_urls[0]
        except:
            return "None"

    except Exception as e:
        logger.error(f"Error scraping image: {str(e)}")
        return "None"

def auto_refresh_news():
    """Auto refresh news from Guardian API with appropriate rate limiting"""
    get_new_news_from_api_and_update()
    interval = 300  # 5 minutes interval
    while True:
        logger.info("Refreshing news from Guardian API...")
        get_new_news_from_api_and_update()
        time.sleep(interval)

# Start the auto-refresh thread
auto_refresh_thread = threading.Thread(target=auto_refresh_news)
auto_refresh_thread.daemon = True
auto_refresh_thread.start()

# Initialize service for individual checks
fake_news_service = GuardianNewsService()

class LiveNewsPrediction(viewsets.ViewSet, RateLimitMixin):
    http_method_names = ('get', 'post', )

    def list(self, request):
        """Handles GET request by displaying all newly retrieved in database."""
        self._wait_for_rate_limit()
        # Get offset from query params, default to 0
        offset = int(request.query_params.get('offset', 0))
        limit = int(request.query_params.get('limit', 10))
        
        # Get paginated news
        all_live_news = LiveNews.objects.all().order_by('-id')[offset:offset + limit]
        total_count = LiveNews.objects.count()
        
        serializer = LiveNewsDetailedSerializer(all_live_news, many=True)
        
        return Response({
            'status': 'success',
            'count': total_count,
            'next_offset': offset + limit if offset + limit < total_count else None,
            'results': serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Get specific news article by ID."""
        self._wait_for_rate_limit()
        try:
            news_prediction = LiveNews.objects.get(pk=pk)
        except LiveNews.DoesNotExist:
            return Response({"error": "News not found"}, status=404)
        
        serializer = LiveNewsDetailedSerializer(news_prediction)
        return Response(serializer.data)

class LiveNewsByCategory(viewsets.ViewSet, RateLimitMixin):
    def list(self, request):
        """Get menu of all available categories."""
        self._wait_for_rate_limit()
        try:
            # Get unique categories from existing news articles
            categories = list(set(LiveNews.objects.values_list('news_category', flat=True)))
            categories.sort()  # Sort alphabetically
            return Response({
                'status': 'success',
                'message': 'Available news categories',
                'categories': categories
            })
            
        except Exception as e:
            logger.error(f"Error getting category menu: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """Get news articles for a specific category."""
        self._wait_for_rate_limit()
        try:
            category_name = pk.replace('-', ' ')
            
            # Get offset from query params, default to 0
            offset = int(request.query_params.get('offset', 0))
            limit = int(request.query_params.get('limit', 10))
            
            # Get total count for this category
            total_count = LiveNews.objects.filter(news_category=category_name).count()
            
            # Get paginated news for category
            live_news = LiveNews.objects.filter(
                news_category=category_name
            ).order_by('-id')[offset:offset + limit]
            
            serializer = LiveNewsDetailedSerializer(live_news, many=True)
            
            return Response({
                'status': 'success',
                'category': category_name,
                'count': total_count,
                'next_offset': offset + limit if offset + limit < total_count else None,
                'results': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error getting category news: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CheckByTitle(viewsets.ViewSet, RateLimitMixin):
    """ViewSet for checking if a news title is fake or real."""
    
    def list(self, request):
        """Handle GET request to show API usage."""
        self._wait_for_rate_limit()
        return Response({
            'status': 'success',
            'message': 'Use POST request with a title parameter to check news',
            'example': {
                'title': 'Your news title here'
            }
        })
    
    def create(self, request):
        """Check if a news title is fake or real."""
        self._wait_for_rate_limit()
        title = request.data.get('title')
        
        if not title:
            return Response(
                {"error": "Title parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        logger.info(f"Checking title: {title}")
        
        try:
            # Get prediction and analysis
            result = fake_news_service.predict_news(title, "")
            
            return Response({
                'status': 'success',
                'title': title,
                'prediction': result['prediction'],
                'confidence': result['confidence'],
                'analysis': result['analysis']
            })
            
        except Exception as e:
            logger.error(f"Error predicting news: {str(e)}")
            return Response(
                {"error": "Error processing prediction"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NewsViewSet(viewsets.ModelViewSet, RateLimitMixin):
    queryset = LiveNews.objects.all()
    serializer_class = NewsSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search news articles by query."""
        self._wait_for_rate_limit()
        try:
            # Get search query and pagination parameters
            query = request.query_params.get('q', '')
            offset = int(request.query_params.get('offset', 0))
            limit = int(request.query_params.get('limit', 10))
            
            # If no query, return latest news instead of error
            if not query:
                queryset = LiveNews.objects.all().order_by('-id')[offset:offset + limit]
                total_count = LiveNews.objects.count()
            else:
                # Search in title and news_category
                queryset = LiveNews.objects.filter(
                    models.Q(title__icontains=query) |
                    models.Q(news_category__icontains=query)
                ).order_by('-id')[offset:offset + limit]
                total_count = LiveNews.objects.filter(
                    models.Q(title__icontains=query) |
                    models.Q(news_category__icontains=query)
                ).count()
            
            # Serialize the results
            serializer = LiveNewsDetailedSerializer(queryset, many=True)
            
            return Response({
                'status': 'success',
                'query': query,
                'count': total_count,
                'next_offset': offset + limit if offset + limit < total_count else None,
                'results': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze news article for fake news detection."""
        self._wait_for_rate_limit()
        try:
            # Validate input
            title = request.data.get('title')
            text = request.data.get('text')
            
            if not title or not text:
                return Response(
                    {'error': 'Both title and text are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get prediction and analysis
            result = fake_news_service.predict_news(title, text)
            
            return Response({
                'status': 'success',
                'prediction': result['prediction'],
                'confidence': f"{result['confidence']:.2%}",
                'probabilities': {
                    'fake': f"{result['probabilities']['fake']:.2%}",
                    'real': f"{result['probabilities']['real']:.2%}"
                },
                'analysis': {
                    'risk_score': f"{result['analysis']['risk_score']:.1f}/100",
                    'patterns': {
                        'caps_usage': result['analysis']['interpretation']['caps_usage'],
                        'punctuation': result['analysis']['interpretation']['punctuation'],
                        'sensationalism': result['analysis']['interpretation']['sensationalism'],
                        'conspiracy_language': result['analysis']['interpretation']['conspiracy_language']
                    }
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )