from django.contrib import admin

from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData, OneTimeEventJob

# Register your models here.
admin.site.register(BigQueryChaptersData)
admin.site.register(BigQueryFirstOpenHomepageData)
admin.site.register(OneTimeEventJob)
