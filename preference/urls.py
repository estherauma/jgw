"""jgwpandas URL Configuration
"""

from django.urls import path
from . import views 



urlpatterns = [
    path("user_overview/", views.user_overview, name="user_overview"),
    path("user_overview/export_stats", views.export_preference_stats, name="export_preference_stats"),
]