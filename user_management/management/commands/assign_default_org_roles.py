from django.core.management.base import BaseCommand

from user_management.models import OrganisationRole, OrganisationRoleAssignment
from user_management.roles import add_default_org_roles
from users.models import User


class Command(BaseCommand):
    help = "Assign default organisation roles for existing users."

    def handle(self, *args, **options):
        users = User.objects.prefetch_related("organisation_data", "groups")
        created = 0
        for user in users.iterator():
            orgs = list(user.organisation_data.all())
            if len(orgs) != 1:
                continue
            organisation = orgs[0]
            add_default_org_roles(organisation)
            if OrganisationRoleAssignment.objects.filter(
                user=user, organisation=organisation
            ).exists():
                continue
            role_qs = OrganisationRole.objects.filter(organisation=organisation)
            if user.groups.filter(name="org_admin").exists():
                role = role_qs.filter(grants_dashboard_access=True).first()
            else:
                role = role_qs.filter(grants_dashboard_access=False).first()
            if not role:
                continue
            OrganisationRoleAssignment.objects.create(
                user=user,
                organisation=organisation,
                role=role,
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Assigned roles for {created} users."))
