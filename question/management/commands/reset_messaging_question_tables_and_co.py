from django.core.management.base import BaseCommand

from question.models import (
    MessagingQuestion,
    MessagingResponse,
    MessagingQuestionResponse,
    MessagingQuestionStandard,
    MessagingQuestionText,
    MessagingResponseOptionText,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        MessagingQuestionStandard.objects.all().delete()
        MessagingQuestion.objects.all().delete()
        MessagingQuestionResponse.objects.all().delete()
        MessagingResponse.objects.all().delete()
        MessagingQuestionText.objects.all().delete()
        MessagingResponseOptionText.objects.all().delete()
        LeadMessagingQuestionResponse.objects.all().delete()
        FollowupMessagingQuestionResponse.objects.all().delete()
        FollowupFollowupMessagingQuestionResponse.objects.all().delete()
        MessagingQuestionV1.objects.all().delete()
        MessagingQuestionResponseV1.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Successfully reset questions tables and co tables"))
