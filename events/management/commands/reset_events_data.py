from django.core.management.base import BaseCommand

from events.models import (
    BigQueryChaptersData, 
    BigQueryFirstOpenHomepageData, 
    ChaptersFeedback, 
    ChaptersFeedbackQuestion, 
    ChaptersFeedbackResponse, 
    ChaptersFeedbackStandard, 
    ChaptersOpened,
    SwsPasiEvent,
    Chapter,
    BigqueryHomepageEventData
)


class Command(BaseCommand):
    """Deletes everything in the imported events tables

    Args:
        BaseCommand (BaseCommand): Django commands base class
        
    Returns: None
    """
    def handle(self, *args, **options):
        ChaptersOpened.objects.all().delete()
        
        ChaptersFeedbackStandard.objects.all().delete()
        ChaptersFeedback.objects.all().delete()
        ChaptersFeedbackResponse.objects.all().delete()
        ChaptersFeedbackQuestion.objects.all().delete()
        Chapter.objects.all().delete()
        
        BigQueryFirstOpenHomepageData.objects.all().delete()
        BigQueryChaptersData.objects.all().delete()
        
        SwsPasiEvent.objects.all().delete()
        BigqueryHomepageEventData.objects.all().delete()
        