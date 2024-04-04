import os


def google_analytics_id(request):
    return {"google_analytics_id": os.environ.get("GTAG_ID")}
