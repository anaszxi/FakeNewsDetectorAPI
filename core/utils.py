import logging
from django.utils.deprecation import MiddlewareMixin
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """Custom exception handler for better error responses."""
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data['status_code'] = response.status_code
        response.data['detail'] = str(exc)
        
    return response

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log all requests and responses."""
    def process_request(self, request):
        logger.info(f"Request: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")
        
    def process_response(self, request, response):
        logger.info(f"Response: {response.status_code} for {request.path}")
        return response 