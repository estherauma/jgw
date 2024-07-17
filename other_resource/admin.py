from django.contrib import admin

from other_resource.models import OtherResource

@admin.register(OtherResource)
class OtherResourceAdminDisplay(admin.ModelAdmin):
    list_display = ["group","title", "description","link","organisation","created_at","updated_at"]
    search_fields = ["group","title", "description","link","organisation","created_at","updated_at"]
    ordering = ["-created_at"]
