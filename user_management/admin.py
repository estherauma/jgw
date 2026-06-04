from django.contrib import admin

from .models import (
    OrganisationRole,
    OrganisationRoleAssignment,
    OrganisationRolePermission,
    ShortLink,
    UserActivity,
    WorkGroup,
    UserActivity,
)


@admin.register(WorkGroup)
class WorkGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation")
    list_select_related = ("organisation",)


@admin.register(OrganisationRole)
class OrganisationRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "grants_dashboard_access", "is_system")
    list_select_related = ("organisation",)
    search_fields = ("name", "organisation__name")


@admin.register(OrganisationRolePermission)
class OrganisationRolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "flag")
    list_select_related = ("role", "flag")
    search_fields = ("role__name", "flag__name")


@admin.register(OrganisationRoleAssignment)
class OrganisationRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "organisation", "role")
    list_select_related = ("user", "organisation", "role")
    search_fields = ("user__email", "organisation__name", "role__name")
@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ("code", "target_url", "expires_at", "created_at")
    list_filter = ("expires_at", "created_at")
    search_fields = ("code", "target_url")


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "actor",
        "action",
        "record_type",
        "record_id",
        "organisation",
        "message",
    )
    list_filter = ("action", "record_type", "created_at")
    list_select_related = ("actor", "organisation")
    search_fields = (
        "actor__email",
        "record_type",
        "record_id",
        "organisation__name",
        "message",
    )
    readonly_fields = (
        "actor",
        "action",
        "record_type",
        "record_id",
        "organisation",
        "message",
        "changes",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False