from django.core.management.base import BaseCommand
from django.core.cache import cache
import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Toggle maintenance mode on/off'

    def add_arguments(self, parser):
        parser.add_argument(
            '--on',
            action='store_true',
            help='Turn maintenance mode on',
        )
        parser.add_argument(
            '--off',
            action='store_true',
            help='Turn maintenance mode off',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current maintenance mode status',
        )

    def handle(self, *args, **options):
        redis_client = redis.from_url(settings.CELERY_BROKER_URL)
        
        try:
            if options['status']:
                status = redis_client.get('MAINTENANCE_MODE')
                status_bool = status is not None and status.decode('utf-8') == 'true'
                self.stdout.write(
                    self.style.SUCCESS(f'Maintenance mode is currently: {"ON" if status_bool else "OFF"}')
                )
                return

            if options['on']:
                redis_client.set('MAINTENANCE_MODE', 'true')
                self.stdout.write(
                    self.style.SUCCESS('Maintenance mode turned ON')
                )
                logger.info("Maintenance mode enabled")
                
            elif options['off']:
                redis_client.set('MAINTENANCE_MODE', 'false')
                self.stdout.write(
                    self.style.SUCCESS('Maintenance mode turned OFF')
                )
                logger.info("Maintenance mode disabled")
                
        except redis.RedisError as e:
            self.stdout.write(
                self.style.ERROR(f'Redis error: {str(e)}')
            )
            logger.error(f"Redis error while toggling maintenance mode: {str(e)}") 