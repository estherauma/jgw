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
            # Check maintenance mode from Redis
            maintenance_mode = self.redis_client.get('MAINTENANCE_MODE')
            maintenance_mode = maintenance_mode is not None and maintenance_mode.decode('utf-8') == 'true'
            
            # Add debug logging
            logger.info(f"Maintenance mode status: {maintenance_mode}")
            logger.info(f"Current request path: {request.path_info}")

            # Check if maintenance mode is enabled
            if maintenance_mode:
                logger.info("Maintenance mode is enabled")
                # Allow superusers to view the site
                if not request.user.is_authenticated or not request.user.is_superuser:
                    # Check if the request path is in the allowed urls
                    allowed_urls = getattr(settings, 'MAINTENANCE_MODE_ALLOWED_URLS', [])
                    if request.path_info not in allowed_urls:
                        logger.info(f"Showing maintenance page to user (path: {request.path_info})")
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