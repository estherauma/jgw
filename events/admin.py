from django.contrib import admin
from events.actions import download_links_click

from events.models import (
    BigQueryChaptersData,
    BigqueryHomepageEventData,
    BigQueryFirstOpenHomepageData,
    ChaptersFeedback,
    ChaptersFeedbackQuestion,
    ChaptersFeedbackResponse,
    ChaptersFeedbackStandard,
    ChaptersOpened,
    TelephoneClickEvent,
    LinksClickEvent,
    OneTimeEventJob,
    SwsPasiEvent,
    Chapter,
    ReportIssueSubmittedEvent,
    UserLocation,
)


class SwsPasiEventTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["event_name"]
    search_fields = ["event_name"]


class ChapterAdminDisplay(admin.ModelAdmin):
    list_display = ["number_key", "chapter_text", "destination"]
    search_fields = ["number_key", "chapter_text"]


@admin.register(ChaptersFeedbackStandard)
class ChaptersFeedbackStandardAdminDisplay(admin.ModelAdmin):
    list_display = [
        "api_created_at",
        "data_source_id",
        "destination",
        "feedback_title",
        "organisation",
        "is_myvoice_organisation",
        "immigration_status",
    ]
    search_fields = ["api_created_at", "data_source_id", "destination", "feedback_title"]
    ordering = ["-api_created_at"]


@admin.register(ChaptersFeedback)
class ChaptersFeedbackAdminDisplay(admin.ModelAdmin):
    list_display = ["feedback_standard", "feedback_question", "feedback_response", "chapter"]
    search_fields = ["feedback_standard", "feedback_question", "feedback_response", "chapter"]
    ordering = ["-feedback_standard"]


# Register your models here.
admin.site.register(BigQueryChaptersData)
admin.site.register(BigQueryFirstOpenHomepageData)
admin.site.register(OneTimeEventJob)
admin.site.register(ChaptersFeedbackQuestion)
admin.site.register(SwsPasiEvent, SwsPasiEventTabularAdminDisplay)
admin.site.register(Chapter, ChapterAdminDisplay)


@admin.register(LinksClickEvent)
class LinksClickEventAdmin(admin.ModelAdmin):
    list_display = ["event_name", "link"]
    actions = [download_links_click]


@admin.register(BigqueryHomepageEventData)
class BigqueryHomepageEventDataAdmin(admin.ModelAdmin):
    list_display = [
        "event_date",
        "device_id",
        "app_id",
        "language",
        "locale",
        "destination",
        "immigration_status",
        "age",
        "organisation",
        "organisation_code",
        "is_myvoice_organisation",
    ]
    ordering = ["event_date"]


@admin.register(TelephoneClickEvent)
class TelephoneClickEventAdmin(admin.ModelAdmin):
    list_display = ["event_name", "link"]
    actions = [download_links_click]


@admin.register(ChaptersOpened)
class ChaptersOpenedAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "event_created_at",
        "event_name",
        "get_chapter_text",
        "get_chapter_key",
        "immigration_status",
        "device_id",
        "destination",
        "organisation",
        "is_myvoice_organisation",
    ]

    def get_chapter_text(self, obj):
        return obj.chapter.chapter_text

    def get_chapter_key(self, obj):
        return obj.chapter.number_key


@admin.register(ChaptersFeedbackResponse)
class ChaptersFeedbackResponseAdmin(admin.ModelAdmin):
    search_fields = ["response", "translated_response"]
    list_display = ["created_at", "response", "translated_response"]
    ordering = ["created_at"]


@admin.register(ReportIssueSubmittedEvent)
class ReportIssueSubmittedEventAdmin(admin.ModelAdmin):
    list_display = (
        "event_date",
        "event_name",
        "device_id",
        "app_id",
        "organisation",
        "destination",
        "origin",
        "language",
        "created_at",
    )
    search_fields = ("device_id", "app_id", "organisation_access_code", "organisation_code", "locale")

@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ["event_date", "created_at", "city", "country", "user_count", "latitude", "longitude"]
    search_fields = ["city", "country"]
    ordering = ["-user_count"]
