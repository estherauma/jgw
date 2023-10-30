from django.contrib import admin

from question.models import (
    MessagingResponse,
    InlineQuestion,
    InlineQuestionResponse,
    InlineQuestionStandard,
    InlineQuestionText,
    InlineQuestionResponseText,
    MessagingQuestion,
    MessagingQuestionResponse,
    MessagingQuestionStandard,
    MessagingQuestionText,
    MessagingResponseOptionText
)

# Register your models here.
admin.site.register(InlineQuestionStandard)
admin.site.register(InlineQuestion)
@admin.register(InlineQuestionText)
class InlineQuestionResponseTextAdminDisplay(admin.ModelAdmin):
    list_display = ['text', 'translated_text', 'title_text']
    search_fields = ['text', 'translated_text', 'title_text']
    
admin.site.register(InlineQuestionResponse)
@admin.register(InlineQuestionResponseText)
class InlineQuestionResponseTextAdminDislay(admin.ModelAdmin):
    list_display = ['text', 'translated_text']
    search_fields = ['text', 'translated_text']

admin.site.register(MessagingQuestionStandard)
admin.site.register(MessagingQuestion)
admin.site.register(MessagingResponse)
admin.site.register(MessagingResponseOptionText)
admin.site.register(MessagingQuestionResponse) 
admin.site.register(MessagingQuestionText)
 

