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
        tag_name = "can_view_what_matters_to_workers_page"

        WaffleFlag = get_waffle_flag_model()
        testers_flag, _ = WaffleFlag.objects.get_or_create(name=tag_name, superusers=True)
        testers_flag.groups.add(testers_group)

        self.stdout.write(self.style.SUCCESS(f'Testers feature flag "{tag_name}" initialized successfully.'))
