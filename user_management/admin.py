from django.contrib import admin

from .models import AppUser, WorkGroup


@admin.register(WorkGroup)
class WorkGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation")
    list_select_related = ("organisation",)


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "organisation_data", "is_active")
    list_select_related = ("organisation_data",)

# Register your models here.
