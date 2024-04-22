from django.contrib import admin
from events.actions import download_links_click

from events.models import (
    BigQueryChaptersData,
    BigQueryFirstOpenHomepageData,
    ChaptersFeedback,
    ChaptersFeedbackQuestion,
    ChaptersFeedbackResponse,
    ChaptersFeedbackStandard,
    ChaptersOpened,
    LinksClickEvent,
    OneTimeEventJob,
    SwsPasiEvent,
    Chapter
)


class SwsPasiEventTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["event_name"]
    search_fields = ["event_name"]


class ChapterAdminDisplay(admin.ModelAdmin):
    list_display = ["number_key", "chapter_text","language","destination"]
    search_fields = ["number_key", "chapter_text","language"]


# Register your models here.
admin.site.register(BigQueryChaptersData)
admin.site.register(BigQueryFirstOpenHomepageData)
admin.site.register(OneTimeEventJob)
admin.site.register(ChaptersFeedbackStandard)
admin.site.register(ChaptersFeedback)
admin.site.register(ChaptersFeedbackQuestion)
admin.site.register(SwsPasiEvent, SwsPasiEventTabularAdminDisplay)
admin.site.register(Chapter, ChapterAdminDisplay)




@admin.register(LinksClickEvent)
class LinksClickEventAdmin(admin.ModelAdmin):
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
        "device_id",
    ]

    def get_chapter_text(self, obj):
        return obj.chapter.chapter_text

    def get_chapter_key(self, obj):
        return obj.chapter.number_key


@admin.register(ChaptersFeedbackResponse)
class ChaptersFeedbackResponseAdmin(admin.ModelAdmin):
    search_fields = ["response", "translated_response"]
    list_display = ["created_at", "response", "translated_response"]
