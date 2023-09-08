from django.core.management.base import BaseCommand

from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData, ChaptersFeedback, ChaptersFeedbackQuestion, ChaptersFeedbackResponse, ChaptersFeedbackStandard, ChaptersOpened


class Command(BaseCommand):
    def handle(self, *args, **options):
        ChaptersOpened.objects.all().delete()
        
        ChaptersFeedbackStandard.objects.all().delete()
        ChaptersFeedback.objects.all().delete()
        ChaptersFeedbackResponse.objects.all().delete()
        ChaptersFeedbackQuestion.objects.all().delete()
        
        BigQueryFirstOpenHomepageData.objects.all().delete()
        BigQueryChaptersData.objects.all().delete()