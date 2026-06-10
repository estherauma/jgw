from django.core.management.base import BaseCommand

from question.models import (
    LeadInlineQuestionResponse,
    FollowupInlineQuestionResponse,
    FollowupFollowupInlineQuestionResponse,
    UniqueInlineQuestion,
)

def reset_inline_question_responses_v3():
    LeadInlineQuestionResponse.objects.all().delete()
    FollowupInlineQuestionResponse.objects.all().delete()
    FollowupFollowupInlineQuestionResponse.objects.all().delete()

    UniqueInlineQuestion.objects.all().delete()

class Command(BaseCommand):
    def handle(self, *args, **options):
        reset_inline_question_responses_v3()
        self.stdout.write(self.style.SUCCESS("Successfully reset inline question responses v3"))
