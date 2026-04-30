from django.contrib import admin
from content.models import AggregatedContent, Collection, Locale, WorkSector

admin.site.register(AggregatedContent)


@admin.register(Locale)
class LocaleTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["code", "name", "created_at", "updated_at", "is_deleted"]
    search_fields = ["name", "code"]
    readonly_fields = ["name", "code", "created_at", "updated_at", "is_deleted"]


@admin.register(WorkSector)
class WorkSectorTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["slug", "display_name", "created_at", "updated_at", "is_deleted"]
    search_fields = ["slug", "display_name"]
    readonly_fields = ["slug", "display_name", "created_at", "updated_at", "is_deleted"]


@admin.register(Collection)
class CollectionTabularAdminDisplay(admin.ModelAdmin):
    list_display = ["name", "api_name", "created_at", "updated_at", "is_deleted"]
    search_fields = ["name", "api_name"]
    readonly_fields = ["name", "api_name", "created_at", "updated_at", "is_deleted"]
