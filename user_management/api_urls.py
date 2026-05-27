from django.urls import path

from user_management.views.api import AccessCodeDetailsApiView, AccessCodeStatusApiView


app_name = "user_management_v1_api"

urlpatterns = [
    path(
        "access-codes/<str:access_code>/status/",
        AccessCodeStatusApiView.as_view(),
        name="access_code_status_api",
    ),
    path(
        "access-codes/<str:access_code>/",
        AccessCodeDetailsApiView.as_view(),
        name="access_code_details_api",
    ),
]
