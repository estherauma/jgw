from django.urls import path

from .views import (activate_account, create_user_account, handle_invite,
                    invite_user, list_users, login_user, logout_user,
                    manage_account, request_password_reset, set_password)

app_name = "users"
urlpatterns = [
    path("", list_users, name="list_users"),
    path("login/", login_user, name="login_user"),
    path("logout/", logout_user, name="logout_user"),
    path("register/", create_user_account, name="create_user"),
    path("manage/<int:id>", manage_account, name="manage_user"),
    path("invite/", invite_user, name="invite_user"),
    path("activate/<int:id>", activate_account, name="activate_account"),
    path("handle_invite/<str:token>", handle_invite, name="handle_invite"),
    path("request_password_reset/", request_password_reset, name="request_password_reset"),
    path("set_password/<str:token>", set_password, name="set_password"),
]
