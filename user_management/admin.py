from django.contrib import admin

from .models import WorkGroup


@admin.register(WorkGroup)
class WorkGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation")
    list_select_related = ("organisation",)


# Register your models here.
