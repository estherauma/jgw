from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [
    # Views
    path("", views.preferences_stats, name="preferences"),
    path("inline-questions", views.inline_question_stats, name="inline"),
    path("messaging-questions", views.messaging_question_stats, name="messaging"),
    path("help-contacts", views.help_contacts_stats, name="help_contacts"),
    path("process-filter-options", views.process_filter_options, name="process_filter_options"),
    path("export/<str:key>", views.export_to_excel_file, name="export_to_excel"),
    # Data for Display
    path("trigger-sentry", views.test_sentry),
]
