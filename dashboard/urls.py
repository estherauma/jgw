from django.urls import path
from . import views

urlpatterns = [
    # Views
    path('', views.preferences_stats ),
    path('inline-questions', views.inline_question_stats),
    path('inline-questions/export', views.export_inline),
    path('preferences/export', views.export_preferences),
    # Data for Display
    path('test-preferences', views.retrieve_preferences),
    path('trigger-sentry', views.test_sentry)
]



