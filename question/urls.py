"""jgwpandas URL Configuration
"""

from django.urls import path
from .views import messaging_question, export_question_stas



urlpatterns = [
    path("messaging/", messaging_question, name="messaging_question"),
    path("messaging/export_stats", export_question_stas, name="export_question_stas"),
]