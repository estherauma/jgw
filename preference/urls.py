"""jgwpandas URL Configuration
"""

from django.urls import path
from . import views 


app_name = "preference"

urlpatterns = [
    path("user-overview/", views.user_overview, name="user_overview"),
    path("user-overview/export-stats", views.export_preference_stats, name="export_preference_stats"),
]