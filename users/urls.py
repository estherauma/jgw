from django.urls import path

from .views import create_user_account, list_users, login_user, logout_user

app_name = "users"
urlpatterns = [
    path("", list_users, name="list_users"),
    path("login/", login_user, name="login_user"),
    path("logout/", logout_user, name="logout_user"),
    path("register/", create_user_account, name="create_user"),
]
