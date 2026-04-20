from django.core.management.base import BaseCommand

from events.models import (
    ChaptersFeedback, 
    ChaptersFeedbackQuestion, 
    ChaptersFeedbackResponse, 
    ChaptersFeedbackStandard, 
)


class Command(BaseCommand):
    """Deletes everything in the chapters feedback tables

    Args:
        BaseCommand (BaseCommand): Django commands base class
        
    Returns: None
    """
    def handle(self, *args, **options):
        ChaptersFeedbackStandard.objects.all().delete()
        ChaptersFeedback.objects.all().delete()
        ChaptersFeedbackResponse.objects.all().delete()
        ChaptersFeedbackQuestion.objects.all().delete()
