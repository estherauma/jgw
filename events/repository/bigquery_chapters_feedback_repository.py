from django.db.models import Count,Q, Count, Case, When, F, Value
from django.db.models import CharField

from events.filters import generic_chapters_feedback_filtered_queryset
from events.models import ChaptersFeedback

def get_chapters_feedback(**filters):

    chapters_feedback_queryset = ChaptersFeedback.objects.filter(
        feedback_response__translated_response__in=["frown", "smile"]
    ).exclude(
        feedback_standard__soft_deleted=True
    ).select_related("feedback_response", "chapter", "immigration_status_chapter_title", "feedback_standard")

    chapters_feedback_queryset = generic_chapters_feedback_filtered_queryset(
        queryset= chapters_feedback_queryset,
        **filters
    )


    chapters_feedback_queryset = chapters_feedback_queryset.annotate(
        display_chapter_text=Case(
            When(immigration_status_chapter_title__chapter_title__isnull=False, then=F('immigration_status_chapter_title__chapter_title')),
            When(chapter__chapter_text__isnull=False, then=F('chapter__chapter_text')),
            default=Value('Others'),
            output_field=CharField()
        ),
        display_number_key=Case(
            When(immigration_status_chapter_title__chapter_title__isnull=False, then=F('immigration_status_chapter_title__chapter_uid')),
            When(chapter__chapter_text__isnull=False, then=F('chapter__number_key')),
            default=Value("Others"),
            output_field=CharField()
        ),
    )

    chapters_feedback_data = chapters_feedback_queryset.values(
        'display_chapter_text'
    ).annotate(
        frowns=Count('id', filter=Q(feedback_response__translated_response="frown")),
        smiles=Count('id', filter=Q(feedback_response__translated_response="smile"))
    )

    return list(chapters_feedback_data)
