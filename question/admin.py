from django.contrib import admin

from question.models import InlineQuestion, InlineQuestionResponse, InlineQuestionStandard, InlineQuestionText, MessagingQuestion, MessagingQuestionOptionResponseAnswer, MessagingQuestionResponse, MessagingQuestionStandard

# Register your models here.
admin.site.register(InlineQuestionStandard)
admin.site.register(InlineQuestion)
admin.site.register(InlineQuestionResponse)
admin.site.register(InlineQuestionText)

admin.site.register(MessagingQuestionStandard)
admin.site.register(MessagingQuestion)
admin.site.register(MessagingQuestionResponse)
admin.site.register(MessagingQuestionOptionResponseAnswer)

