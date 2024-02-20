import os


def expose_template_env_variables(request):
    return {"google_analytics_id": os.environ.get("GTAG_ID")}
