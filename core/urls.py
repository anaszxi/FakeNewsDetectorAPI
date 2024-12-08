from django.urls import path, include
from core.routers import router

urlpatterns = [
    path('api/', include(router.urls)),
]