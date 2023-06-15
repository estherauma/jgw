from django.contrib import admin

from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData

# Register your models here.
admin.site.register(BigQueryChaptersData)
admin.site.register(BigQueryFirstOpenHomepageData)
