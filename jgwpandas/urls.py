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
from user_management.views import short_link_redirect
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from django.conf import settings

admin.site.site_header = settings.ADMIN_SITE_HEADER


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
    path('pipeline/', include('pipeline.urls')),
    path('other-resource/', include('other_resource.urls')),
    path("help-contacts/", include("help_contacts.urls")),
    path("events/", include("events.urls")),
    path("payment/", include("payment.urls")),
    path("api/v1/accounts/", include("users.api_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs-swagger",
    ),
    path("user-management/", include("user_management.urls")),
    path("s/<slug:code>/", short_link_redirect, name="short_link"),
    path("__debug__/", include("debug_toolbar.urls")),

    path('set-language/', set_language, name='set_language'),
    path('api/content/', include('content.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
