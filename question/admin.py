from django.contrib import admin

from question.actions import export_responses
from question.models import (
    FollowUpQuestion,
    MessagingResponse,
    InlineQuestion,
    InlineQuestionResponse,
    InlineQuestionStandard,
    InlineQuestionText,
    InlineQuestionResponseText,
    InlineQuestionAndKeysMatch,
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
    

@admin.register(InlineQuestionAndKeysMatch)
class InlineQuestionAndKeysMatchAdmin(admin.ModelAdmin):
    list_display = ["inline_question","inline_question_key", "custom_lang"]
    search_fields = ["inline_question", "inline_question_key"]

@admin.register(InlineQuestionStandard)
class InlineQuestionStandardAdmin(admin.ModelAdmin):
    list_display = ["id","data_source_id","device_id","destination", "organisation"]
    search_fields = ["id","data_source_id","device_id"]

@admin.register(FollowUpQuestion)
class FollowUpQuestionAdmin(admin.ModelAdmin):
    list_display = ["followup_question_key", "followup_question", "inline_question_text", "custom_lang"]
    search_fields = ["followup_question_key", "followup_question"]

    def inline_question_text(cls, obj):
        return obj.inline_question.inline_question

admin.site.register(InlineQuestionResponse)
# admin.site.register(InlineQuestionStandard)
admin.site.register(MessagingQuestionStandard)
admin.site.register(MessagingQuestion)
admin.site.register(MessagingResponse)
admin.site.register(MessagingResponseOptionText)
admin.site.register(MessagingQuestionResponse)
admin.site.register(MessagingQuestionText)
