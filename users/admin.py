from django.contrib import admin

from users.forms import UserAdminForm
from .models import User, UserInvitations, UserSession

class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm

admin.site.register(User, UserAdmin)


admin.site.register(UserInvitations)

admin.site.register(UserSession)