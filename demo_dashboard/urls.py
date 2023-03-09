from django.urls import path
from . import views

app_name = "demo_dashboard"
urlpatterns = [
    # Views
    path("", views.home, name="home"),
    path("demographics", views.demographics, name="demographics"),
    path("inline-question", views.inline_question, name="inline_question"),
]
