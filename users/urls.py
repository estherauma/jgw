from django.urls import path

from .views import create_user_account, list_users, login_user, logout_user, manage_account, activate_account

app_name = "users"
urlpatterns = [
    path("", list_users, name="list_users"),
    path("login/", login_user, name="login_user"),
    path("logout/", logout_user, name="logout_user"),
    path("register/", create_user_account, name="create_user"),
    path("manage/<int:id>", manage_account, name="manage_user"),
    path("activate/<int:id>", activate_account, name="activate_account"),
]
