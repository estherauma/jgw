from django.contrib import admin

from question.actions import export_responses
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
    MessagingResponseOptionText,
)


@admin.register(InlineQuestionText)
class InlineQuestionResponseTextAdminDisplay(admin.ModelAdmin):
    list_display = ["text", "translated_text", "title_text"]
    search_fields = ["text", "translated_text", "title_text"]


@admin.register(InlineQuestionResponseText)
class InlineQuestionResponseTextAdminDisplay(admin.ModelAdmin):
    list_display = ["translated_text"]
    search_fields = ["translated_text"]


@admin.register(InlineQuestion)
class InlineQuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text", "question_title_text", "question_route"]
    actions = [export_responses]

    @classmethod
    def question_title_text(cls, obj):
        return obj.question.title_text

    @classmethod
    def question_text(cls, obj):
        return obj.question.text

    @classmethod
    def question_route(cls, obj):
        return (
            obj.inline_question_standard.preference.route.name
            if obj.inline_question_standard.preference
            else "not specified"
        )


admin.site.register(InlineQuestionResponse)
admin.site.register(InlineQuestionStandard)
admin.site.register(MessagingQuestionStandard)
admin.site.register(MessagingQuestion)
admin.site.register(MessagingResponse)
admin.site.register(MessagingResponseOptionText)
admin.site.register(MessagingQuestionResponse)
admin.site.register(MessagingQuestionText)
