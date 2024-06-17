from django.contrib import admin
from events.actions import download_links_click

from pipeline.models import CommandLog

@admin.register(CommandLog)
class CommandLogAdminDisplay(admin.ModelAdmin):
    list_display = ["command_name", "data_fetch","command_status","error", "executed_at"]
    search_fields = ["command_name", "data_fetch","command_status","error","executed_at"]
    ordering = ["-executed_at"]

