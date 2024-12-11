"""
WSGI config for FakeNewsDetectorAPI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

# Check if we're running on Azure
settings_module = 'FakeNewsDetectorAPI.deployment' if 'WEBSITE_HOSTNAME' in os.environ else 'FakeNewsDetectorAPI.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
print("Before get_wsgi_application()")
application = get_wsgi_application()
print("After get_wsgi_application()")
