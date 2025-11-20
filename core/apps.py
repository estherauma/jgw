import os
from django.apps import AppConfig
import posthog
import sys


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Initialize PostHog when Django starts.
        PostHog configuration is loaded from environment variables.
        """
        if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv:
            try:

                posthog_api_key = os.getenv('POSTHOG_API_KEY')
                posthog_host = os.getenv('POSTHOG_HOST', 'https://us.i.posthog.com')
                
                if posthog_api_key:
                    posthog.api_key = posthog_api_key
                    posthog.host = posthog_host
            except ImportError:
                pass
