from django.contrib import admin

from .models import (
    OrganisationRole,
    OrganisationRoleAssignment,
    OrganisationRolePermission,
    ShortLink,
    UserActivity,
    WorkGroup,
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


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "log_level", "message", "timestamp")
    list_filter = ("log_level", "timestamp")
    list_select_related = ("user", "organisation")
    search_fields = ("user__email", "message")
    readonly_fields = ("timestamp",)


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ("code", "target_url", "expires_at", "created_at")
    list_filter = ("expires_at", "created_at")
    search_fields = ("code", "target_url")
