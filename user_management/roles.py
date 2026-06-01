from django.contrib.auth.models import Group

from .models import OrganisationRole, OrganisationRoleAssignment

DEFAULT_ROLES = [
    {
        "name": "Administrator",
        "description": "Full access to dashboard management features.",
        "grants_dashboard_access": True,
        "is_system": True,
    },
    {
        "name": "Worker",
        "description": "Standard app access.",
        "grants_dashboard_access": False,
        "is_system": True,
    },
]


def add_default_org_roles(organisation):
    roles = []
    for role_def in DEFAULT_ROLES:
        role, _ = OrganisationRole.objects.get_or_create(
            organisation=organisation,
            name=role_def["name"],
            defaults=role_def,
        )
        roles.append(role)
    return roles


def apply_role_to_user(user, organisation, role):
    assignment, _ = OrganisationRoleAssignment.objects.update_or_create(
        user=user,
        organisation=organisation,
        defaults={"role": role},
    )
    org_admin_group, _ = Group.objects.get_or_create(name="org_admin")
    org_group_admin_group, _ = Group.objects.get_or_create(name="org_group_admin")
    org_staff_group, _ = Group.objects.get_or_create(name="org_staff")
    user_management_group, _ = Group.objects.get_or_create(name="user_management")
    worker_group, _ = Group.objects.get_or_create(name="worker")
    if role.grants_dashboard_access:
        user.access_type = "dashboard"
        user.groups.add(user_management_group)
        if role.is_system:
            user.groups.add(org_admin_group)
            user.groups.remove(org_staff_group, worker_group, org_group_admin_group)
        else:
            user.groups.add(org_staff_group)
            user.groups.remove(org_admin_group, worker_group, org_group_admin_group)
    else:
        user.access_type = "app"
        user.groups.remove(org_admin_group, user_management_group, org_staff_group, org_group_admin_group)
        user.groups.add(worker_group)
    user.save(update_fields=["access_type"])
    return assignment
