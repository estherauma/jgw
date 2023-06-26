from django.contrib import admin

from question.models import InlineQuestion, InlineQuestionResponse, InlineQuestionStandard

# Register your models here.
admin.site.register(InlineQuestionStandard)
admin.site.register(InlineQuestion)
admin.site.register(InlineQuestionResponse)
