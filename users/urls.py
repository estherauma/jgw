from operator import imod
from unicodedata import name
from django.urls import path
from .views import list_users, create_user_account, login_user

app_name='users'
urlpatterns = [
    path("", list_users, name="list_users"),
    path("login/", login_user, name="login_user"),
    path("register/", create_user_account, name="create_user"),
]
