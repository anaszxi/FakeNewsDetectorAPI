"""
Azure deployment settings for FakeNewsDetectorAPI
"""

import os
from .settings import *  # This imports all settings from settings.py
from .settings import BASE_DIR

print("Loading deployment.py")

# Configure the domain name using environment variables
ALLOWED_HOSTS = [os.environ.get('WEBSITE_HOSTNAME', 'fake-news-russ.azurewebsites.net')]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get('WEBSITE_HOSTNAME', 'fake-news-russ.azurewebsites.net')]

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# WhiteNoise configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'NAME': 'mainsql',  # Database name
        'USER': 'dbbadmin',  # MySQL username 
        'PASSWORD': 'd6cTQk2Na6ma7JE',  # MySQL password
        'HOST': 'fake-news-detector-service-dbb.mysql.database.azure.com',
        'PORT': '3306',
        'OPTIONS': {
            'ssl': {
                'ca': os.path.join(BASE_DIR, 'certs', 'DigiCertGlobalRootG2.crt.pem'),  # FIXED SSL CERTIFICATE PATH
                'ssl_disabled': False,  # Enforce SSL connection
            }
        }, 
    }
}

SECURE_SSL_REDIRECT = True

# CORS settings for your mobile app
# CORS_ALLOWED_ORIGINS = [
#    "https://fake-news-russ.azurewebsites.net",
# ]

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

ADMINS = [("anas", "Anasap13@hotmail.com")]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'default from email'

STATIC_ROOT = BASE_DIR / 'staticfiles'
