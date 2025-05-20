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
