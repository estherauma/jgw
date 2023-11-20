from django.core.management.base import BaseCommand

from question.models import (
    InlineQuestion,
    InlineQuestionResponse,
    InlineQuestionStandard,
    InlineQuestionText,
    InlineQuestionResponseText,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        InlineQuestionStandard.objects.all().delete()
        InlineQuestion.objects.all().delete()
        InlineQuestionText.objects.all().delete()
        InlineQuestionResponse.objects.all().delete()
        InlineQuestionResponseText.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Successfully reset questions tables and co tables"))
