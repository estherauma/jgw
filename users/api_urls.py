from django.urls import path

from .api_views import (
    RegisterUserApiView,
    ResendRegistrationCodeApiView,
    VerifyRegistrationCodeApiView,
)

app_name = "user_management_api"

urlpatterns = [
    path("register/", RegisterUserApiView.as_view(), name="register_user_api"),
    path(
        "register/verify-code/",
        VerifyRegistrationCodeApiView.as_view(),
        name="verify_registration_code",
    ),
    path(
        "register/resend-code/",
        ResendRegistrationCodeApiView.as_view(),
        name="resend_registration_code",
    ),
]
