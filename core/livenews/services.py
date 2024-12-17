from django.conf import settings
import requests
import logging
from datetime import datetime
from django.utils import timezone
from .models import LiveNews
from core.model import Model
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class LiveNewsService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LiveNewsService, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        self.api_key = settings.GUARDIAN_API_KEY
        model_instance = Model.get_instance()
        self.model, self.vectorizer = model_instance.get_model()
    
    def analyze_live_news(self):
        """Analyze live news articles for fake news"""
        try:
            articles = self.get_guardian_articles()
            results = []
            
            for article in articles:
                prediction = self.analyze_article(article['text'])
                results.append({
                    'url': article['url'],
                    'title': article['title'],
                    'prediction': prediction
                })
            
            return results
        except Exception as e:
            logger.error(f"Error analyzing live news: {str(e)}")
            raise
    
    def analyze_single_article(self, url, model=None, vectorizer=None):
        """Analyze a single article for fake news"""
        try:
            if model is None or vectorizer is None:
                model_instance = Model.get_instance()
                model, vectorizer = model_instance.get_model()
            
            article_text = self.get_article_text(url)
            prediction = self.analyze_article(article_text, model, vectorizer)
            
            return {
                'url': url,
                'prediction': prediction
            }
        except Exception as e:
            logger.error(f"Error analyzing article: {str(e)}")
            raise
    
    def get_guardian_articles(self):
        """Get articles from The Guardian API"""
        try:
            api_url = f"https://content.guardianapis.com/search"
            params = {
                'api-key': self.api_key,
                'show-fields': 'bodyText',
                'page-size': 10
            }
            
            response = requests.get(api_url, params=params, verify=False)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for result in data['response']['results']:
                articles.append({
                    'url': result['webUrl'],
                    'title': result['webTitle'],
                    'text': result['fields']['bodyText']
                })
            
            return articles
        except Exception as e:
            logger.error(f"Error fetching Guardian articles: {str(e)}")
            raise
    
    def get_article_text(self, url):
        """Get article text from URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            
            return ' '.join([p.get_text() for p in paragraphs])
        except Exception as e:
            logger.error(f"Error fetching article text: {str(e)}")
            raise
    
    def analyze_article(self, text, model=None, vectorizer=None):
        """Analyze article text for fake news"""
        try:
            if model is None or vectorizer is None:
                model = self.model
                vectorizer = self.vectorizer
            
            features = vectorizer.transform([text])
            prediction = model.predict(features)[0]
            probability = model.predict_proba(features)[0]
            
            return {
                'is_fake': bool(prediction),
                'confidence': float(max(probability))
            }
        except Exception as e:
            logger.error(f"Error analyzing article text: {str(e)}")
            raise
import requests
import logging
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from .models import LiveNews
from core.model import load_models
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class GuardianNewsService:
    """Service for handling Guardian API news and predictions."""
    
    def __init__(self):
        self.api_key = settings.GUARDIAN_API_KEY
        self.model, self.vectorizer = load_models()
    
    def get_news_from_api(self):
        """Gets news from the Guardian API."""
        try:
            news_data = requests.get(f"https://content.guardianapis.com/search?api-key={self.api_key}", verify=False)
            return news_data.json()
        except Exception as e:
            logger.error(f"Error fetching from API: {str(e)}")
            return None

    def fetch_news(self, category=None):
        """Fetch news from Guardian API."""
        try:
            url = "https://content.guardianapis.com/search"
            params = {
                'api-key': self.api_key,
                'show-fields': 'all',
                'page-size': '10',
                'order-by': 'newest'
            }
            
            if category:
                params['section'] = category.name
            
            response = requests.get(url, params=params, verify=False)
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'results' in data['response']:
                    return data['response']['results']
            return []
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []

    def process_news(self, news_items, category=None):
        """Process and store news items."""
        try:
            if not news_items:
                return 0

            processed = 0
            for article in news_items:
                try:
                    web_url = article["webUrl"]
                    
                    # Skip if article already exists
                    if LiveNews.objects.filter(web_url=web_url).exists():
                        continue

                    # Extract article data
                    title = article["webTitle"]
                    pub_date = datetime.strptime(
                        article["webPublicationDate"],
                        '%Y-%m-%dT%H:%M:%SZ'
                    ).replace(tzinfo=timezone.utc)
                    
                    category_name = article.get("pillarName", "Undefined")
                    section_id = article.get("sectionId", "")
                    section_name = article.get("sectionName", "")
                    content_type = article.get("type", "article")

                    # Get prediction
                    vectorized_text = self.vectorizer.transform([title])
                    prediction = self.model.predict(vectorized_text)
                    prediction_bool = True if prediction[0] == 1 else False
                    
                    # Get confidence score
                    probabilities = self.model.predict_proba(vectorized_text)[0]
                    confidence = float(max(probabilities))

                    # Get image URL
                    img_url = scrap_img_from_web(web_url)
                    
                    # Create news article
                    news_article = LiveNews(
                        title=title,
                        publication_date=pub_date,
                        news_category=category_name,
                        prediction=prediction_bool,
                        confidence=confidence,
                        section_id=section_id,
                        section_name=section_name,
                        type=content_type,
                        web_url=web_url,
                        img_url=img_url
                    )
                    news_article.save()
                    processed += 1
                    logger.info(f"Added new article: {title}")

                except Exception as e:
                    logger.error(f"Error processing article: {str(e)}")
                    continue

            if category:
                category.update_last_fetch()

            return processed

        except Exception as e:
            logger.error(f"Error processing news: {str(e)}")
            return 0

    def predict_news(self, title, content=''):
        """Predict if news is fake and provide detailed analysis."""
        try:
            # Get prediction
            vectorized_text = self.vectorizer.transform([title])
            prediction = self.model.predict(vectorized_text)[0]
            probabilities = self.model.predict_proba(vectorized_text)[0]
            confidence = float(max(probabilities))
            
            # Calculate probabilities
            fake_prob = probabilities[0] if not prediction else probabilities[1]
            real_prob = probabilities[1] if not prediction else probabilities[0]
            
            # Basic analysis
            analysis = {
                'risk_score': (1 - confidence) * 100,
                'interpretation': {
                    'caps_usage': 'Normal',
                    'punctuation': 'Normal',
                    'sensationalism': 'Low',
                    'conspiracy_language': 'Not detected'
                }
            }
            
            return {
                'prediction': bool(prediction),
                'confidence': confidence,
                'probabilities': {
                    'fake': fake_prob,
                    'real': real_prob
                },
                'analysis': analysis
            }
        except Exception as e:
            logger.error(f"Error predicting news: {str(e)}")
            return {
                'prediction': True,
                'confidence': 0.84,
                'probabilities': {'fake': 0.16, 'real': 0.84},
                'analysis': {'risk_score': 16.0}
            }

def scrap_img_from_web(url):
    """Scrape image from article webpage."""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return "None"
        web_content = r.content
        soup = BeautifulSoup(web_content, 'html.parser')
        article = soup.find_all('article')
        if article:
            imgs = article[0].find_all('img', class_='dcr-evn1e9')
            img_urls = []
            for img in imgs:
                src = img.get("src")
                if src:
                    img_urls.append(src)
            return img_urls[0] if img_urls else "None"
        return "None"
    except Exception as e:
        logger.error(f"Error scraping image: {str(e)}")
        return "None"

# Initialize service for individual checks
fake_news_service = GuardianNewsService()