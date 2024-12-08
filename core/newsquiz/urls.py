from django.urls import path
from .viewsets import NewsQuizViewSet

urlpatterns = [
    path('quiz/random/', NewsQuizViewSet.as_view({'get': 'random'})),
    path('quiz/answer/', NewsQuizViewSet.as_view({'post': 'answer'})),
] 