import logging
from django.shortcuts import render
from django.conf import settings
import redis

logger = logging.getLogger(__name__)

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_client = redis.from_url(settings.CELERY_BROKER_URL)
        logger.info("MaintenanceModeMiddleware initialized")

    def __call__(self, request):
        
        try:

            maintenance_mode = self.redis_client.get('MAINTENANCE_MODE')
            maintenance_mode = maintenance_mode is not None and maintenance_mode.decode('utf-8') == 'true'

            if maintenance_mode:
                if not request.user.is_authenticated or not request.user.is_superuser:

                    allowed_urls = getattr(settings, 'MAINTENANCE_MODE_ALLOWED_URLS', [])
                    if request.path_info not in allowed_urls:
                        context = {
                            'maintenance_message': getattr(
                                settings,
                                'MAINTENANCE_MODE_MESSAGE',
                                'We are currently performing maintenance. Please check back soon.'
                            )
                        }
                        return render(request, 'maintenance/maintenance.html', context, status=503)
            
            return self.get_response(request)
            
        except redis.RedisError as e:
            logger.error(f"Redis error in maintenance middleware: {str(e)}")
            return self.get_response(request) 