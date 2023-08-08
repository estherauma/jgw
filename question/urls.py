"""jgwpandas URL Configuration
"""

from django.urls import path
from .views import (
    messaging_question, 
    export_messaging_question_stats, 
    export_inline_question_stats,
    inline_question
)



urlpatterns = [
    path("messaging/", messaging_question, name="messaging_question"),
    path("messaging/export_messaging_question_stats", export_messaging_question_stats, name="export_messaging_question_stats"),
    
    path("inline/", inline_question, name="inline_question"),
    path("inline/export_inline_question_stats", export_inline_question_stats, name="export_inline_question_stats"),
]