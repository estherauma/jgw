"""jgwpandas URL Configuration
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.utils import OperationalError
from django.db import connection
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


@api_view(["GET"])
def health(request):
    heath_params = {"app server": "active"}
    try:
        connection.ensure_connection()
        heath_params["database"] = "active"
    except OperationalError:
        heath_params["database"] = "down"
    return Response(heath_params)


urlpatterns = [
    # admin site
    path("admin/", admin.site.urls),
    # dashboard
    path("", include("dashboard.urls")),
    # accounts
    path("accounts/", include("users.urls")),
    path("health/", health),
    path("question/", include("question.urls")),
    path("preference/", include("preference.urls")),
    path("help-contacts/", include("help_contacts.urls")),
    path("events/", include("events.urls")),
    path("payment/", include("payment.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)