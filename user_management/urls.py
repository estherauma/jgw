from django.urls import path
from .views import user_management


app_name = "user_management"

urlpatterns = [
    path('', user_management, name="home"),

]
