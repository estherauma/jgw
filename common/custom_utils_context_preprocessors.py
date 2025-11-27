import os
from django.conf import settings


def google_analytics_id(request):
    """
    Context processor to expose Google Analytics ID to templates
    """
    try:
        gtag_id = getattr(settings, 'GTAG_ID', None)
        if not gtag_id:
            gtag_id = os.environ.get('GTAG_ID', '')
        return {"google_analytics_id": gtag_id}
    except Exception:
        return {"google_analytics_id": ""}


def posthog_web_config(request):
    """
    Expose PostHog configuration for front-end error tracking / analytics.
    """
    try:
        return {
            "posthog_project_api_key": getattr(settings, "POSTHOG_PROJECT_API_KEY", ""),
            "posthog_host": getattr(settings, "POSTHOG_HOST", "https://us.i.posthog.com"),
            "posthog_defaults_date": getattr(settings, "POSTHOG_DEFAULTS_DATE", ""),
            "posthog_web_enabled": getattr(settings, "POSTHOG_WEB_ENABLED", False),
            "posthog_skip_local": getattr(settings, "POSTHOG_SKIP_LOCALHOST", True),
        }
    except Exception:
        return {
            "posthog_project_api_key": "",
            "posthog_host": "https://us.i.posthog.com",
            "posthog_defaults_date": "",
            "posthog_web_enabled": False,
            "posthog_skip_local": True,
        }
