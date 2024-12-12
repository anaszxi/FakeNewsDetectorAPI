
import os

from django.core.wsgi import get_wsgi_application

settings_module = 'core.deployment' if 'WEBSITE_HOSTNAME' in os.environ else 'core.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
print("Before get_wsgi_application()")
application = get_wsgi_application()
print("After get_wsgi_application()")
