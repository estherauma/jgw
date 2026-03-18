from django.contrib import admin

from users.forms import UserAdminForm
from .models import User, UserInvitations, UserSession
from import_export.admin import ExportActionModelAdmin

class UserAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    form = UserAdminForm
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'password', 'first_name', 'last_name', 'role', 'scheme')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Relationships', {
            'fields': ('factories', 'organisations', 'organisation_data', 'destinations', 
                      'user_languages', 'excluded_origin_countries', 'immigration_status')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'is_active', 'groups')
        }),
        ('Preferences', {
            'fields': ('receive_marketing_emails', 'dashboard_preferences', 'dashboard_preferences_version')
        }),
        ('Statistics', {
            'fields': ('total_logged_hours',)
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by')
        }),
    )

admin.site.register(User, UserAdmin)


admin.site.register(UserInvitations)

admin.site.register(UserSession)