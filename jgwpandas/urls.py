"""jgwpandas URL Configuration
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from rest_framework.decorators import api_view
from django.db.utils import OperationalError
from django.db import connection
from django.http import JsonResponse


@api_view(["GET"])
def health(request):
    heath_params = {"app server": "active"}
    try:
        connection.ensure_connection()
        heath_params["database"] = "active"
    except OperationalError:
        heath_params["database"] = "down"

    return JsonResponse(heath_params)


urlpatterns = [
    # admin site
    path("admin/", admin.site.urls),
    # dashboard
    path("", include("dashboard.urls")),
    # accounts
    path("accounts/", include("users.urls")),
]
