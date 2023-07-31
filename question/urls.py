"""jgwpandas URL Configuration
"""

from django.urls import path
from .views import messaging_question, export_question_stats



urlpatterns = [
    path("messaging/", messaging_question, name="messaging_question"),
    path("export_question_stats_to_excel/<str:question_type>", export_question_stats, name="export_question_stats_to_excel"),
]