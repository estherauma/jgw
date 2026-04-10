from django.contrib import admin

from users.forms import UserAdminForm
from .models import User, UserInvitations, UserSession
from import_export.admin import ExportActionModelAdmin

class UserAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    form = UserAdminForm
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ('created_at_display', 'updated_at_display', 'total_logged_hours', 'deleted_at', 'deleted_by')
    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'password', 'first_name', 'last_name', 'role', 'access_type', 'scheme', 'phone_number', 'phone_country_iso')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Relationships', {
            'fields': ('factories', 'organisations', 'organisation_data', 'work_groups', 'destinations',
                      'user_languages', 'excluded_origin_countries', 'immigration_status')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'is_active', 'is_deleted', 'groups')
        }),
        ('Preferences', {
            'fields': ('receive_marketing_emails', 'dashboard_preferences', 'dashboard_preferences_version')
        }),
        ('Statistics', {
            'fields': ('total_logged_hours',)
        }),
        ('Audit', {
            'fields': ('created_at_display', 'updated_at_display', 'created_by', 'updated_by', 'deleted_at', 'deleted_by')
        }),
    )

    @admin.display(description='Created at')
    def created_at_display(self, obj):
        return obj.created_at

    @admin.display(description='Updated at')
    def updated_at_display(self, obj):
        return obj.updated_at

admin.site.register(User, UserAdmin)


admin.site.register(UserInvitations)

admin.site.register(UserSession)
