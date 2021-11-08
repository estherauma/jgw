from django.urls import path
from . import views

urlpatterns = [
    # Views
    path('', views.index ),
    path('inline-questions', views.inline),
    # Data for Display
    path('analytics/preferences', views.preferences_stats),
    path('analytics/inline-questions', views.inline_stats),
    path('test-preferences', views.retrieve_preferences),
    path('trigger-sentry', views.test_sentry)
]
