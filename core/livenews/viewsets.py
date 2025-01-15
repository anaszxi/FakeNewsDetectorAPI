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

def get_new_news_from_api_and_update():
    """Gets news from the guardian news using it's API"""
    news_data = requests.get("https://content.guardianapis.com/search?api-key=e705adff-ca49-414e-89e2-7edede919e2e")
    news_data = news_data.json()

    news_titles = [article["webTitle"] for article in news_data["response"]["results"]]
    news_publication_dates = [article["webPublicationDate"] for article in news_data["response"]["results"]]
    news_categories = []

    for article in news_data["response"]["results"]:
        try:
            news_categories.append(article["pillarName"])
        except KeyError:
            news_categories.append("Undefined")

    section_id = [article["sectionId"] for article in news_data["response"]["results"]]
    section_name = [article["sectionName"] for article in news_data["response"]["results"]]
    type = [article["type"] for article in news_data["response"]["results"]]
    web_url = [article["webUrl"] for article in news_data["response"]["results"]]

    nb_model, vect_model = load_models()

    for i in range(len(news_titles)):
        try:
            title_ = news_titles[i]
            publication_date_str = news_publication_dates[i]
            
            # Convert string to datetime with timezone
            try:
                publication_date_ = datetime.strptime(publication_date_str, '%Y-%m-%dT%H:%M:%SZ')
                publication_date_ = timezone.make_aware(publication_date_)
            except ValueError:
                logger.error(f"Invalid date format: {publication_date_str}")
                continue
                
            category_ = news_categories[i]
            section_id_ = section_id[i]
            section_name_ = section_name[i]
            type_ = type[i]
            web_url_ = web_url[i]

            if not LiveNews.objects.filter(web_url=web_url_).exists():
                vectorized_text = vect_model.transform([title_])
                prediction = nb_model.predict(vectorized_text)
                prediction_bool = True if prediction[0] == 1 else False

                img_url_ = scrap_img_from_web(web_url_)
                
                news_article = LiveNews(
                    title=title_,
                    publication_date=publication_date_,
                    news_category=category_,
                    prediction=prediction_bool,
                    section_id=section_id_,
                    section_name=section_name_,
                    type=type_,
                    web_url=web_url_,
                    img_url=img_url_
                )
                news_article.save()
        except Exception as e:
            logger.error(f"Error processing article {i}: {str(e)}")
            continue

def scrap_img_from_web(url):
    print(url)
    r = requests.get(url)
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

def auto_refresh_news():
    get_new_news_from_api_and_update()
    interval = 10
    while True:
        print("Thread running!")
        get_new_news_from_api_and_update()
        time.sleep(interval)

# Start the auto-refresh thread
auto_refresh_thread = threading.Thread(target=auto_refresh_news)
auto_refresh_thread.daemon = True
auto_refresh_thread.start()

# Initialize service for individual checks
fake_news_service = GuardianNewsService()

class LiveNewsPrediction(viewsets.ViewSet):
    http_method_names = ('get', 'post', )

    def list(self, request):
        """Handles GET request by displaying all newly retrieved in database."""
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
        try:
            news_prediction = LiveNews.objects.get(pk=pk)
        except LiveNews.DoesNotExist:
            return Response({"error": "News not found"}, status=404)
        
        serializer = LiveNewsDetailedSerializer(news_prediction)
        return Response(serializer.data)

class LiveNewsByCategory(viewsets.ViewSet):
    def list(self, request):
        """Get menu of all available categories."""
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

class CheckByTitle(viewsets.ViewSet):
    """ViewSet for checking if a news title is fake or real."""
    
    def list(self, request):
        """Handle GET request to show API usage."""
        return Response({
            'status': 'success',
            'message': 'Use POST request with a title parameter to check news',
            'example': {
                'title': 'Your news title here'
            }
        })
    
    def create(self, request):
        """Check if a news title is fake or real."""
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

class NewsViewSet(viewsets.ModelViewSet):
    queryset = LiveNews.objects.all()
    serializer_class = NewsSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search news articles by query."""
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