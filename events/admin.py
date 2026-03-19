from django.contrib import admin
from events.actions import download_links_click
from import_export.admin import ExportActionModelAdmin

from events.models import (
    BigQueryChaptersData,
    BigqueryHomepageEventData,
    BigQueryFirstOpenHomepageData,
    ChaptersFeedback,
    ChaptersFeedbackQuestion,
    ChaptersFeedbackResponse,
    ChaptersFeedbackStandard,
    ChaptersOpened,
    ImmigrationStatusChapterTitle,
    TelephoneClickEvent,
    LinksClickEvent,
    OneTimeEventJob,
    SwsPasiEvent,
    Chapter,
    ReportIssueSubmittedEvent,
    UserLocation,
)
from preference.models import PreferenceHistory


class SwsPasiEventTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["event_name"]
    search_fields = ["event_name"]


class ChapterAdminDisplay(admin.ModelAdmin):
    list_display = ["number_key", "chapter_text", "destination", "origin"]
    search_fields = ["number_key", "chapter_text"]


@admin.register(ChaptersFeedbackStandard)
class ChaptersFeedbackStandardAdminDisplay(ExportActionModelAdmin, admin.ModelAdmin):
    list_display = [
        "id",
        "api_created_at",
        "data_source_id",
        "documentId",
        "destination",
        "feedback_title",
        "organisation",
        "org_code",
        "org_info",
        "is_myvoice_organisation",
        "immigration_status",
        "is_org_info_cleaned",
        "soft_deleted",
    ]
    search_fields = ["api_created_at", "data_source_id", "destination", "feedback_title", "documentId"]
    ordering = ["-api_created_at"]


@admin.register(ChaptersFeedback)
class ChaptersFeedbackAdminDisplay(admin.ModelAdmin):
    list_display = ["feedback_standard", "feedback_question", "feedback_response", "chapter", "immigration_status_chapter_title"]
    search_fields = ["feedback_standard", "feedback_question", "feedback_response", "chapter", "immigration_status_chapter_title"]
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
    list_display = ["event_date", "event_name", "link"]
    actions = [download_links_click]


@admin.register(BigqueryHomepageEventData)
class BigqueryHomepageEventDataAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    list_display = [
        "event_date",
        "device_id",
        "app_id",
        "language",
        "locale",
        "preference",
        "destination",
        "immigration_status",
        "age",
        "organisation",
        "org_info",
        "organisation_code",
        "geo_city",
        "geo_country",
        "is_myvoice_organisation",
        "is_org_info_cleaned",
    ]
    ordering = ["-event_date"]


@admin.register(TelephoneClickEvent)
class TelephoneClickEventAdmin(admin.ModelAdmin):
    list_display = ["event_name", "link"]
    actions = [download_links_click]


@admin.register(ChaptersOpened)
class ChaptersOpenedAdmin(admin.ModelAdmin):
    search_fields = ["event_name", "chapter__chapter_text", "chapter__number_key", "destination", "organisation", "org_info"]
    list_display = [
        "created_at",
        "event_created_at",
        "event_name",
        "chapter",
        "get_chapter_text",
        "get_chapter_key",
        "immigration_status_chapter_title",
        "immigration_status",
        "device_id",
        "destination",
        "origin",
        "org_code",
        "organisation",
        "org_info",
        "is_myvoice_organisation",
        "is_org_info_cleaned",
    ]

    def get_chapter_text(self, obj):
        return obj.chapter.chapter_text if obj.chapter else None

    def get_chapter_key(self, obj):
        return obj.chapter.number_key if obj.chapter else None
    
    def get_immigration_status_chapter_title(self, obj):
        return obj.immigration_status_chapter_title.chapter_title if obj.immigration_status_chapter_title else None


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
    list_display = ["event_date", "created_at", "user_pseudo_id", "country"]
    search_fields = ["user_pseudo_id", "country__name"]
    ordering = ["-created_at"]

@admin.register(ImmigrationStatusChapterTitle)
class ImmigrationStatusChapterTitleAdmin(admin.ModelAdmin):
    list_display = ["immigration_status", "destination", "documentId", "chapter_uid", "chapter_title"]
    search_fields = ["immigration_status", "destination", "documentId", "chapter_uid", "chapter_title"]
