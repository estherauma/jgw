"""jgwpandas URL Configuration
"""

from django.urls import path
from .views import (
    export_inline_question_data,
    export_messaging_question_data,
    messaging_question,
    export_messaging_question_stats,
    export_inline_question_stats,
    inline_question,
    export_message_sent_data,
    export_payment_inline_questions,
)


app_name = "question"

urlpatterns = [
    path("messaging/", messaging_question, name="messaging_question"),
    path(
        "messaging/export-messaging-question-stats",
        export_messaging_question_stats,
        name="export_messaging_question_stats",
    ),
    path(
        "messaging/export-messaging-question-data/",
        export_messaging_question_data,
        name="export_messaging_question_data",
    ),
    path("inline/", inline_question, name="inline_question"),
    path(
        "inline/export-inline-question-stats",
        export_inline_question_stats,
        name="export_inline_question_stats",
    ),
    path(
        "inline/export_inline_question_data/", export_inline_question_data, name="export_inline_question_data"
    ),
    path("export-message-sent-data/", export_message_sent_data, name="export_message_sent_data"),
    path(
        "inline/export_payment_inline_questions/", export_payment_inline_questions, name="export_payment_inline_questions"
    ),
]
