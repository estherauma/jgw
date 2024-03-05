from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from waffle import get_waffle_flag_model


class Command(BaseCommand):
    help = "Create initial featrure toggle tags for the testers group using the waffle library"

    def handle(self, *args, **options):

        # Create testers group
        group_name = "testers"

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
            "can_view_what_matters_to_workers_page",
            "can_view_messaging_questions_page",
            "can_view_inline_questions_page",
            "can_view_new_monthly_users_chart",
            "can_view_get_users_by_country_state_chart",
            "users-by-sector-graph-id",
        ]

        WaffleFlag = get_waffle_flag_model()
        for flag_name in flags_list:
            created_flag, created = WaffleFlag.objects.get_or_create(name=flag_name, superusers=True)
            created_flag.groups.add(testers_group)

            self.stdout.write(
                self.style.SUCCESS(f'Testers feature flag "{flag_name}" initialized successfully.')
            )
