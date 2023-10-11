from django.contrib import admin

from users.forms import UserAdminForm
from .models import User, UserInvitations

class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm

admin.site.register(User, UserAdmin)


admin.site.register(UserInvitations)
