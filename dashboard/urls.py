from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [
    # Views
    path("app_events", views.app_events_stats, name="app_events"),
    path("", views.home, name="home"),
    path("preferences", views.preferences_stats, name="preferences"),
    path("inline", views.inline_question_stats, name="inline"),
    path("messaging-questions", views.messaging_question_stats, name="messaging"),
    path("filter-data/<str:category>", views.filter_data, name="filter_data"),
    path("help-contacts", views.help_contacts_stats, name="help_contacts"),
    path("export-report", views.export_report, name="export_report"),
    path("checklists/<str:key>", views.checklists_stats, name="checklists"),
    path("process-origin-options/<str:key>", views.process_origin_options, name="process_origin_options"),
    path("process-factory-options/<str:key>", views.process_factory_options, name="process_factory_options"),
    path("export/<str:key>", views.export_to_excel_file, name="export_to_excel"),
    path("trigger-sentry", views.test_sentry),
]
