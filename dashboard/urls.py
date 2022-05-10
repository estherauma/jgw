from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [
    # Views
    path("", views.preferences_stats, name="index"),
    path("inline-questions", views.inline_question_stats, name="inline_question_stats"),
    path("messaging-questions", views.messaging_question_stats, name="messaging_question_stats"),
    path("help-contacts", views.help_contacts_stats, name="help_contacts_stats"),
    path("process-filter-options", views.process_filter_options, name="process_filter_options"),
    path("inline-questions/export", views.export_inline),
    path("preferences/export", views.export_preferences),
    # Data for Display
    path("test-preferences", views.retrieve_preferences),
    path("trigger-sentry", views.test_sentry),
]
