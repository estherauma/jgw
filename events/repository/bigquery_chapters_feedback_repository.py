from collections import defaultdict
from django.db.models import Count, Sum, Q, Count, Case, When, IntegerField, F
from django.db.models import Value, CharField

from events.filters import generic_chapters_feedback_filtered_queryset
from events.models import Chapter, ChaptersFeedback, ChaptersFeedbackStandard


def get_chapters_feedback(**filters):
    """Aggregates chapters feedback and returns a dictionary"""
    chapters_opened_queryset = generic_chapters_feedback_filtered_queryset(
        queryset=ChaptersFeedback.objects.select_related("feedback_response", "chapter").filter(
            feedback_response__translated_response__in=["frown", "smile"]
        ),
        **filters
    )

    chapters_feedback_data = chapters_opened_queryset.annotate(
        chapter_text=Case(
            When(chapter__chapter_text__isnull=True, then=F("chapter__number_key")),
            default=F("chapter__chapter_text"),
            output_field=CharField()
        )
    ).values(
        chapter_text=F("chapter_text")
    ).annotate(
        frowns=Count(
            Case(When(feedback_response__translated_response="frown", then=1), output_field=IntegerField())
        ),
        smiles=Count(
            Case(When(feedback_response__translated_response="smile", then=1), output_field=IntegerField())
        ),
    )

    return list(chapters_feedback_data)