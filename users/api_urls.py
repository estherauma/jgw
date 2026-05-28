from django.urls import path

from .api_views import (
    CurrentUserApiView,
    LoginApiView,
    RefreshTokenApiView,
    RegisterUserApiView,
    ResendRegistrationCodeApiView,
    VerifyRegistrationCodeApiView,
)

app_name = "users_api"

urlpatterns = [
    path("me/", CurrentUserApiView.as_view(), name="me_api"),
    path("login/", LoginApiView.as_view(), name="login_api"),
    path("token/refresh/", RefreshTokenApiView.as_view(), name="refresh_token_api"),
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
