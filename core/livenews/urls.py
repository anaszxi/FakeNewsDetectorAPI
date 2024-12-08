from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import LiveNewsPrediction, LiveNewsByCategory, CheckByTitle, NewsViewSet

router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')
router.register(r'check', CheckByTitle, basename='check')
router.register(r'category', LiveNewsByCategory, basename='category')
router.register(r'live', LiveNewsPrediction, basename='live')

urlpatterns = [
    path('', include(router.urls)),
] 