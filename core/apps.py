import os
from django.apps import AppConfig
from posthog import Posthog
import sys


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Initialize PostHog when Django starts.
        PostHog configuration is loaded from environment variables.
        Exception autocapture requires PostHog SDK v3.7.0 or higher.
        """
        if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv:
            try:
                posthog_api_key = os.getenv('POSTHOG_API_KEY')
                posthog_host = os.getenv('POSTHOG_HOST', 'https://us.i.posthog.com')
                
                if posthog_api_key:
                        self.posthog = Posthog(
                            posthog_api_key,
                            host=posthog_host,
                            enable_exception_autocapture=True
                        )
            except ImportError:
                pass
