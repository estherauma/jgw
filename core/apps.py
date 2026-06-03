import os
import sys

from django.apps import AppConfig
from django.conf import settings

try:
    import posthog
except ImportError:
    posthog = None


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Initialize PostHog when Django starts.
        PostHog configuration is loaded from environment variables.
        Exception autocapture requires PostHog SDK v3.7.0 or higher.
        """
        import common.signals

        if posthog is None:
            return

        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return

        posthog_api_key = getattr(settings, 'POSTHOG_PROJECT_API_KEY', None)
        posthog_host = getattr(settings, 'POSTHOG_HOST', os.getenv('POSTHOG_HOST', 'https://us.i.posthog.com'))

        if not posthog_api_key:
            return

        posthog.project_api_key = posthog_api_key
        posthog.host = posthog_host
        posthog.disabled = False
        posthog.debug = bool(getattr(settings, 'DEBUG', False))
