from django.core.management.base import BaseCommand

from question.models import (
    InlineQuestion, 
    InlineQuestionResponse, 
    InlineQuestionStandard, 
    InlineQuestionText,
    MessagingQuestion,
    MessagingQuestionOptionResponseAnswer,
    MessagingQuestionResponse, 
    MessagingQuestionStandard
)



class Command(BaseCommand):
    def handle(self, *args, **options):
        InlineQuestionStandard.objects.all().delete()
        InlineQuestion.objects.all().delete()
        InlineQuestionText.objects.all().delete()
        InlineQuestionResponse.objects.all().delete()
        
        MessagingQuestionStandard.objects.all().delete()
        MessagingQuestion.objects.all().delete()
        MessagingQuestionResponse.objects.all().delete()
        MessagingQuestionOptionResponseAnswer.objects.all().delete()
    
        self.stdout.write(self.style.SUCCESS('Successfully reset questions tables and co tables'))