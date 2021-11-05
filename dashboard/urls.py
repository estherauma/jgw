from django.urls import path
from . import views

urlpatterns = [
    path('', views.index ),
    path('analytics/preferences', views.preferences_stats),
    path('test-preferences', views.retrieve_preferences),
    path('trigger-sentry', views.test_sentry)
]
