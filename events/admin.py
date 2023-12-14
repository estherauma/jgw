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
    Chapter,
)


class SwsPasiEventTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["event_name"]
    search_fields = ["event_name"]


class ChapterAdminDisplay(admin.ModelAdmin):
    list_display = ["number_key", "chapter_text"]


# Register your models here.
admin.site.register(BigQueryChaptersData)
admin.site.register(BigQueryFirstOpenHomepageData)
admin.site.register(OneTimeEventJob)

admin.site.register(ChaptersOpened)

admin.site.register(ChaptersFeedbackStandard)
admin.site.register(ChaptersFeedback)
admin.site.register(ChaptersFeedbackResponse)
admin.site.register(ChaptersFeedbackQuestion)
admin.site.register(SwsPasiEvent, SwsPasiEventTabularAdminDisplay)
admin.site.register(Chapter, ChapterAdminDisplay)


@admin.register(LinksClickEvent)
class LinksClickEventAdmin(admin.ModelAdmin):
    list_display = ["event_name", "link"]
    actions = [download_links_click]
