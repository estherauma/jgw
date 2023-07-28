"""jgwpandas URL Configuration
"""

from django.urls import path
from .views import messaging_question



urlpatterns = [
    path("messaging/", messaging_question, name="messaging_question"),
]