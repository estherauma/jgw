from collections import defaultdict
from django.db.models import Count, Sum, Q

from events.models import Chapter, ChaptersFeedback, ChaptersFeedbackStandard


def get_chapters_feedback():
    """Aggregates chapters feedback and returns a disctionary"""
    chapter_counts = Chapter.objects.annotate(
        frowns=Count(
            "chapterfeedback_chapters__feedback_response",
            filter=Q(chapterfeedback_chapters__feedback_response__translated_response__icontains="frown"),
        ),
        smiles=Count(
            "chapterfeedback_chapters__feedback_response",
            filter=Q(chapterfeedback_chapters__feedback_response__translated_response__icontains="smile"),
        ),
    ).values("number_key", "frowns", "smiles")

    return list(chapter_counts)
