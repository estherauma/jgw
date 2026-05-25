from django.contrib import admin

from .models import (
    OrganisationRole,
    OrganisationRoleAssignment,
    OrganisationRolePermission,
    ShortLink,
    UserVerificationCode,
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


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ("code", "target_url", "expires_at", "created_at")
    list_filter = ("expires_at", "created_at")
    search_fields = ("code", "target_url")


@admin.register(UserVerificationCode)
class UserVerificationCodeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "purpose",
        "attempts",
        "max_attempts",
        "expires_at",
        "used_at",
        "created_at",
    )
    list_select_related = ("user",)
    list_filter = ("purpose", "expires_at", "used_at", "created_at")
    search_fields = ("user__email", "user__phone_number", "purpose")
    readonly_fields = ("code_hash", "created_at", "used_at")
