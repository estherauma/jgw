from import_export import resources
from users.models import User

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser')