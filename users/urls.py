from django.urls import path

from .views import (
    activate_account,
    change_email_address,
    create_user_account,
    verify_invite,
    invite_user,
    list_invitations,
    list_users,
    login_user,
    logout_user,
    manage_account,
    profile,
    request_password_reset,
    set_password,
    verify_email_change,
)

app_name = "users"
urlpatterns = [
    path("", list_users, name="list_users"),
    path("login/", login_user, name="login_user"),
    path("logout/", logout_user, name="logout_user"),
    path("register/", create_user_account, name="create_user"),
    path("manage/<int:id>", manage_account, name="manage_user"),
    path("invite/", invite_user, name="invite_user"),
    path("invitations/", list_invitations, name="list_invitations"),
    path("activate/<int:id>", activate_account, name="activate_account"),
    path("verify/invite/<str:token>", verify_invite, name="verify_invite"),
    path("request_password_reset/", request_password_reset, name="request_password_reset"),
    path("set_password/<str:token>", set_password, name="set_password"),
    path("profile/", profile, name="profile"),
    path("verify/email/<str:token>", verify_email_change, name='verify_email'),
    path("change_email/", change_email_address, name='change_email')
]
