from django.urls import path
from . import views

app_name = "demo_dashboard"
urlpatterns = [
    # Views
    path("", views.home, name="home"),
]
