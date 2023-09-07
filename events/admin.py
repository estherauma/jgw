from django.contrib import admin

from events.models import (
    BigQueryChaptersData, 
    BigQueryFirstOpenHomepageData,
    ChaptersFeedback,
    ChaptersFeedbackQuestion,
    ChaptersFeedbackResponse,
    ChaptersFeedbackStandard, 
    ChaptersOpened, 
    OneTimeEventJob
)

# Register your models here.
admin.site.register(BigQueryChaptersData)
admin.site.register(BigQueryFirstOpenHomepageData)
admin.site.register(OneTimeEventJob)
admin.site.register(ChaptersOpened)

admin.site.register(ChaptersFeedbackStandard)
admin.site.register(ChaptersFeedback)
admin.site.register(ChaptersFeedbackResponse)
admin.site.register(ChaptersFeedbackQuestion)