from django.contrib import admin
from import_export.admin import ExportActionModelAdmin

from question.actions import export_responses
from question.user_insights_admin import (
    UserInsightsIndicatorAdminForm,
    UserInsightsIndicatorInlineQuestionAdminForm,
    UserInsightsIndicatorMessagingQuestionAdminForm,
    sync_indicator_inline_questions,
    sync_indicator_messaging_questions,
)
from question.models import (
    UniqueInlineQuestion,
    UniqueMessagingQuestion,
    UserInsightsIndicator,
    UserInsightsIndicatorInlineQuestion,
    UserInsightsIndicatorMessagingQuestion,
    UserInsightsReport,
    ActualMessageSent,
    FollowUpQuestion,
    FollowupFollowupInlineQuestionResponse,
    FollowupInlineQuestionResponse,
    LeadInlineQuestionResponse,
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
    QuestionCategory,
    LeadMessagingQuestionResponse,
    FollowupMessagingQuestionResponse,
    FollowupFollowupMessagingQuestionResponse,
    MessagingQuestionV1,
    MessagingQuestionResponseV1,
    InlineQuestionV1,
    InlineQuestionResponseV1,
)
from question.resources import InlineQuestionResource, MessagingQuestionResource


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
class InlineQuestionStandardAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    resource_class = InlineQuestionResource
    list_display = [
        "api_created_at",
        "api_updated_at",
        "id",
        "data_source_id",
        "device_id",
        "destination",
        "organisation",
        "org_info",
        "org_code",
        "is_myvoice_organisation",
        "is_org_info_cleaned",
    ]
    search_fields = ["id", "data_source_id", "device_id", "org_code"]


@admin.register(FollowUpQuestion)
class FollowUpQuestionAdmin(admin.ModelAdmin):
    list_display = ["followup_question_key", "followup_question", "inline_question_text", "custom_lang"]
    search_fields = ["followup_question_key", "followup_question"]

    def inline_question_text(cls, obj):
        return obj.inline_question.inline_question


@admin.register(MessagingQuestionStandard)
class MessagingQuestionStandardAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    resource_class = MessagingQuestionResource
    list_display = [
        "api_created_at",
        "data_source_id",
        "device_id",
        "question_id",
        "is_test_data",
        "question_version",
        "route",
        "preference",
        "factory_farm",
        "locale",
        "language",
        "destination",
        "organisation_sector",
        "get_sectors_of_work",
        "organisation",
        "org_code",
        "org_info",
        "is_org_info_cleaned",
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
        "org_code",
        "is_myvoice_organisation",
        "immigration_status",
    ]
    ordering = ["-api_created_at"]

    def get_sectors_of_work(self, obj):
        return ", ".join([sector.display_name for sector in obj.sectors_of_work.all()])
    get_sectors_of_work.short_description = "Sectors of Work"


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

@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "created_at", "updated_at"]
    search_fields = ["name", "code"]

@admin.register(LeadMessagingQuestionResponse)
class LeadMessagingQuestionResponseAdmin(admin.ModelAdmin):
    list_display = [
        "api_created_at", 
        "data_source_id", 
        "device_id", 
        "get_question_indicators",
        "get_question_key", 
        "get_question_text", 
        "questionresponsetype",
        "get_response_key", 
        "get_response_text",
        "org_info", 
        "immigration_status", 
        "language", 
        "destination", 
        "locale", 
        "get_question_category", 
        "created_at", 
        "updated_at"
    ]
    search_fields = [
        "data_source_id", 
        "device_id",
        "messaging_question__question_key",
        "messaging_question__question_text",
        "messaging_question_response__response_key",
        "messaging_question_response__response_text",
        "messaging_question__question_category__name",
        "messaging_question__question_category__code"
    ]
    ordering = ["-api_created_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("question_indicators")

    @admin.display(description="Question indicators")
    def get_question_indicators(self, obj):
        indicators = list(obj.question_indicators.all())
        if not indicators:
            return "—"
        labels = [str(indicator) for indicator in indicators[:5]]
        if len(indicators) > 5:
            labels.append(f"+{len(indicators) - 5} more")
        return ", ".join(labels)

    def get_question_key(self, obj):
        return obj.messaging_question.question_key if obj.messaging_question else None
    get_question_key.short_description = "Question Key"

    def get_question_text(self, obj):
        return obj.messaging_question.question_text if obj.messaging_question else None
    get_question_text.short_description = "Question Text"

    def get_response_key(self, obj):
        return obj.messaging_question_response.response_key if obj.messaging_question_response else None
    get_response_key.short_description = "Response Key"

    def get_response_text(self, obj):
        return obj.messaging_question_response.response_text if obj.messaging_question_response else None
    get_response_text.short_description = "Response Text"

    def get_question_category(self, obj):
        if obj.messaging_question and obj.messaging_question.question_category:
            return obj.messaging_question.question_category.name
        return None
    get_question_category.short_description = "Question Category"

@admin.register(FollowupMessagingQuestionResponse)
class FollowupMessagingQuestionResponseAdmin(admin.ModelAdmin):
    list_display = [
        "api_created_at", 
        "data_source_id", 
        "device_id", 
        "lead_question",
        "get_question_key", 
        "get_question_text", 
        "questionresponsetype",
        "get_response_key", 
        "get_response_text", 
        "get_question_category", 
        "created_at", 
        "updated_at"
    ]
    search_fields = [
        "data_source_id", 
        "device_id",
        "messaging_question__question_key",
        "messaging_question__question_text",
        "messaging_question_response__response_key",
        "messaging_question_response__response_text",
        "messaging_question__question_category__name",
        "messaging_question__question_category__code"
    ]
    ordering = ["-api_created_at"]

    def get_question_key(self, obj):
        return obj.messaging_question.question_key if obj.messaging_question else None
    get_question_key.short_description = "Question Key"

    def get_question_text(self, obj):
        return obj.messaging_question.question_text if obj.messaging_question else None
    get_question_text.short_description = "Question Text"

    def get_response_key(self, obj):
        return obj.messaging_question_response.response_key if obj.messaging_question_response else None
    get_response_key.short_description = "Response Key"

    def get_response_text(self, obj):
        return obj.messaging_question_response.response_text if obj.messaging_question_response else None
    get_response_text.short_description = "Response Text"

    def get_question_category(self, obj):
        if obj.messaging_question and obj.messaging_question.question_category:
            return obj.messaging_question.question_category.name
        return None
    get_question_category.short_description = "Question Category"

@admin.register(FollowupFollowupMessagingQuestionResponse)
class FollowupFollowupMessagingQuestionResponseAdmin(admin.ModelAdmin):
    list_display = [
        "api_created_at", 
        "data_source_id", 
        "device_id", 
        "followup_question",
        "get_question_key", 
        "get_question_text", 
        "questionresponsetype",
        "get_response_key", 
        "get_response_text", 
        "get_question_category", 
        "question_response_date", 
        "created_at", 
        "updated_at"
    ]
    search_fields = [
        "data_source_id", 
        "device_id",
        "messaging_question__question_key",
        "messaging_question__question_text",
        "messaging_question_response__response_key",
        "messaging_question_response__response_text",
        "messaging_question__question_category__name",
        "messaging_question__question_category__code"
    ]
    ordering = ["-api_created_at"]

    def get_question_key(self, obj):
        return obj.messaging_question.question_key if obj.messaging_question else None
    get_question_key.short_description = "Question Key"

    def get_question_text(self, obj):
        return obj.messaging_question.question_text if obj.messaging_question else None
    get_question_text.short_description = "Question Text"

    def get_response_key(self, obj):
        return obj.messaging_question_response.response_key if obj.messaging_question_response else None
    get_response_key.short_description = "Response Key"

    def get_response_text(self, obj):
        return obj.messaging_question_response.response_text if obj.messaging_question_response else None
    get_response_text.short_description = "Response Text"

    def get_question_category(self, obj):
        if obj.messaging_question and obj.messaging_question.question_category:
            return obj.messaging_question.question_category.name
        return None
    get_question_category.short_description = "Question Category"

@admin.register(LeadInlineQuestionResponse)
class LeadInlineQuestionResponseAdmin(admin.ModelAdmin):
    list_display = [
        "api_created_at", 
        "data_source_id", 
        "device_id", 
        "get_question_indicators",
        "get_question_key", 
        "get_question_text", 
        "questionresponsetype",
        "get_response_key", 
        "get_response_text",
        "organisation", 
        "organisation_code", 
        "immigration_status", 
        "factory_farm", 
        "language", 
        "destination", 
        "locale", 
        "get_question_category", 
        "created_at", 
        "updated_at"
    ]
    search_fields = [
        "api_created_at", 
        "data_source_id", 
        "device_id",
        "inline_question__question_key",
        "inline_question__question_text",
        "inline_question_response__response_key",
        "inline_question_response__response_text",
        "inline_question__question_category__name",
        "inline_question__question_category__code",
        "organisation_code",
        "immigration_status__name",
        "factory_farm__name",
        "language__name",
        "destination__name",
        "locale__name"
    ]
    ordering = ["-api_created_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("question_indicators")

    @admin.display(description="Question indicators")
    def get_question_indicators(self, obj):
        indicators = list(obj.question_indicators.all())
        if not indicators:
            return "—"
        labels = [str(indicator) for indicator in indicators[:5]]
        if len(indicators) > 5:
            labels.append(f"+{len(indicators) - 5} more")
        return ", ".join(labels)

    def get_question_key(self, obj):
        return obj.inline_question.question_key if obj.inline_question else None
    get_question_key.short_description = "Question Key"

    def get_question_text(self, obj):
        return obj.inline_question.question_text if obj.inline_question else None
    get_question_text.short_description = "Question Text"

    def get_response_key(self, obj):
        return obj.inline_question_response.response_key if obj.inline_question_response else None
    get_response_key.short_description = "Response Key"

    def get_response_text(self, obj):
        return obj.inline_question_response.response_text if obj.inline_question_response else None
    get_response_text.short_description = "Response Text"

    def get_question_category(self, obj):
        if obj.inline_question and obj.inline_question.question_category:
            return obj.inline_question.question_category.name
        return None
    get_question_category.short_description = "Question Category"

@admin.register(FollowupInlineQuestionResponse)
class FollowupInlineQuestionResponseAdmin(admin.ModelAdmin):
    list_display = [
        "api_created_at", 
        "data_source_id", 
        "device_id", 
        "lead_question",
        "get_question_key", 
        "get_question_text", 
        "questionresponsetype",
        "get_response_key", 
        "get_response_text", 
        "get_question_category", 
        "question_response_date", 
        "created_at", 
        "updated_at"
    ]
    search_fields = [
        "api_created_at", 
        "data_source_id", 
        "device_id",
        "inline_question__question_key",
        "inline_question__question_text",
        "inline_question_response__response_key",
        "inline_question_response__response_text",
        "inline_question__question_category__name",
        "inline_question__question_category__code"
    ]
    ordering = ["-api_created_at"]

    def get_question_key(self, obj):
        return obj.inline_question.question_key if obj.inline_question else None
    get_question_key.short_description = "Question Key"

    def get_question_text(self, obj):
        return obj.inline_question.question_text if obj.inline_question else None
    get_question_text.short_description = "Question Text"

    def get_response_key(self, obj):
        return obj.inline_question_response.response_key if obj.inline_question_response else None
    get_response_key.short_description = "Response Key"

    def get_response_text(self, obj):
        return obj.inline_question_response.response_text if obj.inline_question_response else None
    get_response_text.short_description = "Response Text"

    def get_question_category(self, obj):
        if obj.inline_question and obj.inline_question.question_category:
            return obj.inline_question.question_category.name
        return None
    get_question_category.short_description = "Question Category"

@admin.register(FollowupFollowupInlineQuestionResponse)
class FollowupFollowupInlineQuestionResponseAdmin(admin.ModelAdmin):
    list_display = [
        "api_created_at", 
        "data_source_id", 
        "device_id", 
        "followup_question",
        "get_question_key", 
        "get_question_text", 
        "questionresponsetype",
        "get_response_key", 
        "get_response_text", 
        "get_question_category", 
        "question_response_date", 
        "created_at", 
        "updated_at"
    ]
    search_fields = [
        "api_created_at", 
        "data_source_id", 
        "device_id",
        "inline_question__question_key",
        "inline_question__question_text",
        "inline_question_response__response_key",
        "inline_question_response__response_text",
        "inline_question__question_category__name",
        "inline_question__question_category__code"
    ]
    ordering = ["-api_created_at"]

    def get_question_key(self, obj):
        return obj.inline_question.question_key if obj.inline_question else None
    get_question_key.short_description = "Question Key"

    def get_question_text(self, obj):
        return obj.inline_question.question_text if obj.inline_question else None
    get_question_text.short_description = "Question Text"

    def get_response_key(self, obj):
        return obj.inline_question_response.response_key if obj.inline_question_response else None
    get_response_key.short_description = "Response Key"

    def get_response_text(self, obj):
        return obj.inline_question_response.response_text if obj.inline_question_response else None
    get_response_text.short_description = "Response Text"

    def get_question_category(self, obj):
        if obj.inline_question and obj.inline_question.question_category:
            return obj.inline_question.question_category.name
        return None
    get_question_category.short_description = "Question Category"

admin.site.register(MessagingQuestion)
admin.site.register(MessagingResponse)
admin.site.register(MessagingResponseOptionText)
admin.site.register(MessagingQuestionText)

@admin.register(MessagingQuestionV1)
class MessagingQuestionV1Admin(admin.ModelAdmin):
    list_display = ["page_id", "page_title", "question_key", "question_text", "question_category", "created_at", "updated_at"]
    search_fields = ["page_id", "question_key", "question_text", "question_category__name", "question_category__code"]
    ordering = ["-created_at"]

@admin.register(MessagingQuestionResponseV1)
class MessagingQuestionResponseV1Admin(admin.ModelAdmin):
    list_display = ["response_key", "response_text", "response_text_translated", "created_at", "updated_at"]
    search_fields = ["response_key", "response_text", "response_text_translated"]
    ordering = ["-created_at"]

@admin.register(InlineQuestionV1)
class InlineQuestionV1Admin(admin.ModelAdmin):
    list_display = ["page_id", "page_title", "question_key", "question_text", "question_category", "created_at", "updated_at"]
    search_fields = ["page_id", "question_key", "question_text", "question_category__name", "question_category__code"]
    ordering = ["-created_at"]

@admin.register(InlineQuestionResponseV1)
class InlineQuestionResponseV1Admin(admin.ModelAdmin):
    list_display = ["response_key", "response_text", "response_text_translated", "created_at", "updated_at"]
    search_fields = ["response_key", "response_text", "response_text_translated"]
    ordering = ["-created_at"]


class UserInsightsIndicatorInline(admin.TabularInline):
    model = UserInsightsIndicator
    extra = 0
    fields = [
        "slug",
        "name",
        "color",
        "breakdown_index",
        "show_on_donut",
        "donut_slot",
        "display_order",
        "is_active",
    ]
    show_change_link = True


@admin.register(UniqueInlineQuestion)
class UniqueInlineQuestionAdmin(admin.ModelAdmin):
    list_display = ["question_key", "question_text", "updated_at"]
    search_fields = ["question_key", "question_text"]
    ordering = ["question_key"]


@admin.register(UniqueMessagingQuestion)
class UniqueMessagingQuestionAdmin(admin.ModelAdmin):
    list_display = ["question_key", "question_text", "updated_at"]
    search_fields = ["question_key", "question_text"]
    ordering = ["question_key"]


@admin.register(UserInsightsReport)
class UserInsightsReportAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "display_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["slug", "title"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [UserInsightsIndicatorInline]


@admin.register(UserInsightsIndicator)
class UserInsightsIndicatorAdmin(admin.ModelAdmin):
    form = UserInsightsIndicatorAdminForm
    list_display = [
        "name",
        "report",
        "slug",
        "breakdown_index",
        "inline_question_count",
        "messaging_question_count",
        "show_on_donut",
        "donut_slot",
        "is_active",
    ]
    list_filter = ["report", "is_active", "show_on_donut"]
    search_fields = ["name", "slug", "report__slug"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "report",
                    "slug",
                    "name",
                    "color",
                    "display_order",
                    "breakdown_index",
                    "show_on_donut",
                    "donut_slot",
                    "is_active",
                ),
            },
        ),
        (
            "Inline questions",
            {
                "fields": ("inline_questions",),
                "classes": ("wide",),
                "description": (
                    "Select all lead inline questions for this indicator. "
                    "Run sync_unique_lead_questions if the list is empty."
                ),
            },
        ),
        (
            "Messaging questions",
            {
                "fields": ("messaging_questions",),
                "classes": ("wide",),
                "description": (
                    "Select all lead messaging questions for this indicator."
                ),
            },
        ),
    )

    @admin.display(description="Inline Qs")
    def inline_question_count(self, obj):
        return obj.indicator_inline_questions.count()

    @admin.display(description="Messaging Qs")
    def messaging_question_count(self, obj):
        return obj.indicator_messaging_questions.count()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        sync_indicator_inline_questions(
            obj, form.cleaned_data.get("inline_questions", [])
        )
        sync_indicator_messaging_questions(
            obj, form.cleaned_data.get("messaging_questions", [])
        )


@admin.register(UserInsightsIndicatorInlineQuestion)
class UserInsightsIndicatorInlineQuestionAdmin(admin.ModelAdmin):
    form = UserInsightsIndicatorInlineQuestionAdminForm
    list_display = [
        "indicator",
        "report_title",
        "question_key_display",
        "question_text_display",
        "updated_at",
    ]
    list_filter = ["indicator__report", "indicator"]
    list_select_related = ("indicator", "indicator__report", "question")
    search_fields = [
        "indicator__name",
        "indicator__slug",
        "indicator__report__title",
        "question__question_key",
        "question__question_text",
    ]
    autocomplete_fields = ["indicator"]
    ordering = ["indicator__report__title", "indicator__name", "question__question_key"]
    fieldsets = (
        (
            None,
            {
                "fields": ("indicator", "questions"),
                "classes": ("wide",),
                "description": (
                    "Pick an indicator, then check every inline question that belongs to it. "
                    "Saving replaces all inline links for that indicator."
                ),
            },
        ),
    )

    @admin.display(description="Report", ordering="indicator__report__title")
    def report_title(self, obj):
        return obj.indicator.report.title

    @admin.display(description="Question key", ordering="question__question_key")
    def question_key_display(self, obj):
        return obj.question.question_key

    @admin.display(description="Question text", ordering="question__question_text")
    def question_text_display(self, obj):
        return obj.question.question_text

    def save_model(self, request, obj, form, change):
        indicator = form.cleaned_data["indicator"]
        sync_indicator_inline_questions(
            indicator, form.cleaned_data.get("questions", [])
        )
        link = indicator.indicator_inline_questions.order_by("pk").first()
        if link:
            obj.pk = link.pk
            obj.indicator = link.indicator
            obj.question = link.question

    def save_form(self, request, form, change):
        return form.save(commit=False)

    def response_add(self, request, obj, post_url_continue=None):
        if obj.pk:
            return super().response_add(request, obj, post_url_continue)
        return self.response_post_save_add(request, obj)

    def response_change(self, request, obj):
        if obj.pk:
            return super().response_change(request, obj)
        return self.response_post_save_change(request, obj)


@admin.register(UserInsightsIndicatorMessagingQuestion)
class UserInsightsIndicatorMessagingQuestionAdmin(admin.ModelAdmin):
    form = UserInsightsIndicatorMessagingQuestionAdminForm
    list_display = [
        "indicator",
        "report_title",
        "question_key_display",
        "question_text_display",
        "updated_at",
    ]
    list_filter = ["indicator__report", "indicator"]
    list_select_related = ("indicator", "indicator__report", "question")
    search_fields = [
        "indicator__name",
        "indicator__slug",
        "indicator__report__title",
        "question__question_key",
        "question__question_text",
    ]
    autocomplete_fields = ["indicator"]
    ordering = ["indicator__report__title", "indicator__name", "question__question_key"]
    fieldsets = (
        (
            None,
            {
                "fields": ("indicator", "questions"),
                "classes": ("wide",),
                "description": (
                    "Pick an indicator, then check every messaging question that belongs to it. "
                    "Saving replaces all messaging links for that indicator."
                ),
            },
        ),
    )

    @admin.display(description="Report", ordering="indicator__report__title")
    def report_title(self, obj):
        return obj.indicator.report.title

    @admin.display(description="Question key", ordering="question__question_key")
    def question_key_display(self, obj):
        return obj.question.question_key

    @admin.display(description="Question text", ordering="question__question_text")
    def question_text_display(self, obj):
        return obj.question.question_text

    def save_model(self, request, obj, form, change):
        indicator = form.cleaned_data["indicator"]
        sync_indicator_messaging_questions(
            indicator, form.cleaned_data.get("questions", [])
        )
        link = indicator.indicator_messaging_questions.order_by("pk").first()
        if link:
            obj.pk = link.pk
            obj.indicator = link.indicator
            obj.question = link.question

    def save_form(self, request, form, change):
        return form.save(commit=False)

    def response_add(self, request, obj, post_url_continue=None):
        if obj.pk:
            return super().response_add(request, obj, post_url_continue)
        return self.response_post_save_add(request, obj)

    def response_change(self, request, obj):
        if obj.pk:
            return super().response_change(request, obj)
        return self.response_post_save_change(request, obj)
