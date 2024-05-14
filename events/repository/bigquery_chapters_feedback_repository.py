from django.db.models import Count,Q, Count, Case, When, F
from django.db.models import CharField

from events.filters import generic_chapters_feedback_filtered_queryset
from events.models import ChaptersFeedback

def get_chapters_feedback(**filters):
    chapters_feedback_queryset = generic_chapters_feedback_filtered_queryset(
        queryset=ChaptersFeedback.objects.filter(
            feedback_response__translated_response__in=["frown", "smile"]
        ).select_related("feedback_response", "chapter"),
        **filters
    )

    chapters_feedback_data = chapters_feedback_queryset.values(
        chapter_text=Case(
            When(chapter__chapter_text__isnull=True, then=F("chapter__number_key")),
            default=F("chapter__chapter_text"),
            output_field=CharField()
        ),
        number_key=F("chapter__number_key")
    ).annotate(
        frowns=Count('id', filter=Q(feedback_response__translated_response="frown")),
        smiles=Count('id', filter=Q(feedback_response__translated_response="smile"))
    )

    return list(chapters_feedback_data)
