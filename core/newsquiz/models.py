from django.db import models
import random
from core.model import load_models  # Import the Model class from model.py
import numpy as np

# Load the trained model and vectorizer once to avoid reloading for each request
model_instance = load_models()
model, vectorizer = model_instance

class NewsQuizManager(models.Manager):
    """A model manager to retrieve data from model and use AI model for predictions."""

    def get_random_news(self):
        """Gets random news from the database."""
        count = self.count()
        if count == 0:
            return None
        random_index = random.randint(0, count - 1)
        return self.all()[random_index]

    def get_label_of_news(self, news_id):
        """Get the label of a news article by its ID (database label)."""
        try:
            news = self.get(id=news_id)
            return news.label
        except self.model.DoesNotExist:
            return None

    def predict_news_label(self, news_text):
        """Uses the trained model to predict if a news article is fake or real."""
        if model is None or vectorizer is None:
            raise ValueError("Model or vectorizer is not loaded properly.")

        # Transform text using vectorizer
        news_vector = vectorizer.transform([news_text])

        # Predict label (0 = Fake, 1 = Real)
        prediction = model.predict(news_vector)
        return bool(prediction[0])  # Convert NumPy value to Python boolean

class NewsQuizData(models.Model):
    """A model to store news articles for quiz generation."""
    news_title = models.CharField(max_length=2000)
    news_description = models.TextField()
    label = models.BooleanField()

    objects = NewsQuizManager()

    def __str__(self):
        return self.news_title
