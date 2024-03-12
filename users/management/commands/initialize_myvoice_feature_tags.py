from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from waffle import get_waffle_flag_model


class Command(BaseCommand):
    help = "Create initial featrure toggle tags for the my voice group using the waffle library"

    def handle(self, *args, **options):

        group_name = "my_voice"

        testers_group, _ = Group.objects.get_or_create(name=group_name)
        permissions = Permission.objects.filter(
            ~Q(content_type__app_label="users")
            & ~Q(content_type__app_label="admin")
            & ~Q(content_type__app_label="waffle")
            & ~Q(content_type__app_label="auth")
        )
        for permission in permissions:
            testers_group.permissions.add(permission)

        # initialize testers feature tag
        flags_list = [
            "can_view_get_users_by_country_state_chart",
        ]

        WaffleFlag = get_waffle_flag_model()
        for flag_name in flags_list:
            created_flag, _ = WaffleFlag.objects.get_or_create(name=flag_name, superusers=True)
            created_flag.groups.add(testers_group)

            self.stdout.write(
                self.style.SUCCESS(f'My voice feature flag "{flag_name}" initialized successfully.')
            )
