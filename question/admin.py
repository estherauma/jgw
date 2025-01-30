from django.contrib import admin

from question.actions import export_responses
from question.models import (
    ActualMessageSent,
    FollowUpQuestion,
    MessageDataSent,
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


@admin.register(InlineQuestionResponse)
class InlineQuestionResponseAdmin(admin.ModelAdmin):
    list_display = ["inline_question", "organisation_inline_question", "response", "created_at", "updated_at"]
    search_fields = ["organisation_inline_question"]
    ordering = ["-created_at"]


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
    list_display = ["inline_question", "inline_question_key", "custom_lang"]
    search_fields = ["inline_question", "inline_question_key"]


@admin.register(InlineQuestionStandard)
class InlineQuestionStandardAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "data_source_id",
        "device_id",
        "destination",
        "organisation",
        "is_myvoice_organisation",
    ]
    search_fields = ["id", "data_source_id", "device_id"]


@admin.register(FollowUpQuestion)
class FollowUpQuestionAdmin(admin.ModelAdmin):
    list_display = ["followup_question_key", "followup_question", "inline_question_text", "custom_lang"]
    search_fields = ["followup_question_key", "followup_question"]

    def inline_question_text(cls, obj):
        return obj.inline_question.inline_question


@admin.register(MessagingQuestionStandard)
class MessagingQuestionStandardAdmin(admin.ModelAdmin):
    list_display = [
        "api_created_at",
        "data_source_id",
        "device_id",
        "question_id",
        "route",
        "factory_farm",
        "destination",
        "organisation_sector",
        "organisation",
        "is_myvoice_organisation",
        "immigration_status",
    ]
    search_fields = [
        "api_created_at",
        "data_source_id",
        "device_id",
        "question_id",
        "route",
        "factory_farm",
        "destination",
        "organisation_sector",
        "organisation",
        "is_myvoice_organisation",
        "immigration_status",
    ]
    ordering = ["-api_created_at"]


@admin.register(MessagingQuestionResponse)
class MessagingQuestionResponseAdmin(admin.ModelAdmin):
    list_display = ["messaging_question", "created_at", "updated_at"]
    search_fields = ["messaging_question"]
    ordering = ["-created_at"]


@admin.register(MessageDataSent)
class MessageDataSentAdmin(admin.ModelAdmin):
    list_display = [
        "api_created_at",
        "device_id",
        "message_id",
        "message_content",
        "destination",
        "organisation",
        "language",
        "message_title_english",
        "message_title",
        "message_date",
        "message_delivered_date",
        "message_queued",
        "message_delivered",
        "message_notification_sent_to_fcm",
    ]
    search_fields = ["device_id", "message_id", "message_title"]
    ordering = ["-message_date"]


@admin.register(ActualMessageSent)
class ActualMessageSentAdmin(admin.ModelAdmin):
    list_display = ["message_id", "message", "created_at", "updated_at"]
    search_fields = ["message_id", "message"]
    ordering = ["-created_at"]


admin.site.register(MessagingQuestion)
admin.site.register(MessagingResponse)
admin.site.register(MessagingResponseOptionText)
admin.site.register(MessagingQuestionText)

