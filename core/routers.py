from rest_framework.routers import DefaultRouter
from core.livenews.viewsets import (
    LiveNewsPrediction,
    LiveNewsByCategory,
    CheckByTitle,
    NewsViewSet
)
from core.newsquiz.viewsets import NewsQuizViewSet

router = DefaultRouter()
router.register(r'live', LiveNewsPrediction, basename='live')
router.register(r'category', LiveNewsByCategory, basename='category')
router.register(r'check', CheckByTitle, basename='check')
router.register(r'news', NewsViewSet, basename='news')
router.register(r'quiz', NewsQuizViewSet, basename='quiz')

urlpatterns = [
    *router.urls,
]