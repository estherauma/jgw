from django.core.management.base import BaseCommand

from question.models import (
    InlineQuestion,
    InlineQuestionResponse,
    InlineQuestionStandard,
    InlineQuestionText,
    InlineQuestionResponseText,
    InlineQuestionV1,
    InlineQuestionResponseV1,
)

def reset_inline_questions_and_dependant_tabels():
    InlineQuestionStandard.objects.all().delete()
    InlineQuestion.objects.all().delete()
    InlineQuestionText.objects.all().delete()
    InlineQuestionResponse.objects.all().delete()
    InlineQuestionResponseText.objects.all().delete()
    InlineQuestionV1.objects.all().delete()
    InlineQuestionResponseV1.objects.all().delete()
    UniqueInlineQuestion.objects.all().delete()
    

class Command(BaseCommand):
    def handle(self, *args, **options):
        reset_inline_questions_and_dependant_tabels()
        self.stdout.write(self.style.SUCCESS("Successfully reset questions tables and co tables"))
