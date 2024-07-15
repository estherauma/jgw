"""jgwpandas URL Configuration
"""

from django.urls import path
from . import views 


app_name = "preference"

urlpatterns = [
    path("user-overview/", views.user_overview, name="user_overview"),
    path("user-overview/export-stats", views.export_preference_stats, name="export_preference_stats"),
    path('user-overview/export-returning-users/', views.export_returning_users_to_excel, name='export_returning_users'),
    path('user-overview/export-help-contacts/', views.export_help_contacts_data, name='export_help_contacts'),
    path('user-overview/export-preferences', views.export_preferences_data, name='export_preferences')
]