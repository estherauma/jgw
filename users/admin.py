from django.contrib import admin

from users.forms import UserAdminForm
from .models import User, UserInvitations
from import_export.admin import ExportActionModelAdmin
class UserAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    form = UserAdminForm

admin.site.register(User, UserAdmin)


admin.site.register(UserInvitations)
