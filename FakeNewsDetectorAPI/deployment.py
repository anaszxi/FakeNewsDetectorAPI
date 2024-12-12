"""
Azure deployment settings for FakeNewsDetectorAPI
"""

import os
from .settings import *  # This imports all settings from settings.py
print("Loading deployment.py")

# Configure the domain name using the environment variable
ALLOWED_HOSTS = [
    'fake-news-app22.azurewebsites.net',
    'localhost',
    '127.0.0.1'
]

CSRF_TRUSTED_ORIGINS = [
    'https://fake-news-app22.azurewebsites.net',
]

# WhiteNoise configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add CORS middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configure MySQL database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('AZURE_MYSQL_NAME', 'fake-news-detector-service-dbb'),
        'USER': os.environ.get('AZURE_MYSQL_USER', 'dbbadmin'),
        'PASSWORD': os.environ.get('AZURE_MYSQL_PASSWORD'),
        'HOST': os.environ.get('AZURE_MYSQL_HOST', 'fake-news-detector-service-dbb.mysql.database.azure.com'),
        'PORT': '3306',
        'OPTIONS': {
            'ssl': {'ssl-mode': 'require'}
        }
    }
}

# Azure Blob Storage Settings
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER_NAME = 'models'
MODEL_BLOB_NAME = 'model_1_5_2.pkl'
LOCAL_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model_1_5_2.pkl')

# SECURITY SETTINGS
DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS settings for your mobile app
CORS_ALLOWED_ORIGINS = [
    "https://fake-news-app22.azurewebsites.net",
]
CORS_ALLOW_CREDENTIALS = True

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
