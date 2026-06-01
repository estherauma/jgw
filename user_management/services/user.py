from users.models import User, UserInvitations
from user_management.models import WorkGroup

from user_management.services.organization import OrganizationService
from user_management.roles import add_default_org_roles, apply_role_to_user
from user_management.utils import (
    get_active_role,
    get_group_names,
    is_org_admin_or_staff,
    is_org_group_admin,
    is_super_or_58_admin,
)


def assign_default_app_registration_membership(user, organisation):
    add_default_org_roles(organisation)
    worker_role = organisation.roles.filter(name__iexact="Worker").first()
    user.organisation_data.add(organisation)
    apply_role_to_user(user, organisation, worker_role)
    return {"role": worker_role}


def get_user_role_display(user, selected_org=None):
    role = get_active_role(user)
    if role == "super_user":
        return "Super Admin"
    if role == "58_admin":
        return "Fiftyeight Admin"
    if role == "org_group_admin":
        return "Organization Group Admin"
    if role == "org_admin":
        return "Administrator" if selected_org else "Org Admin"
    if role == "org_staff":
        assignment = user.org_roles.all().first()
        if assignment and assignment.role:
            return assignment.role.name
    if "worker" in get_group_names(user):
        return "Worker"
    return "—"


def get_users_query(current_user, selected_org=None):
    users = (
        User.objects.prefetch_related(
            "groups",
            "organisation_data",
            "work_groups",
            "org_roles__role",
            "org_roles__organisation",
        )
        .select_related("organization_group")
        .order_by("-created_at")
        .distinct()
    )
    if selected_org:
        users = users.filter(organisation_data=selected_org)

    if is_org_admin_or_staff(current_user):
        allowed_orgs = OrganizationService.get_allowed_orgs(current_user)
        users = users.filter(organisation_data__in=allowed_orgs).distinct()
    for user in users:
        user.role_display = get_user_role_display(user, selected_org=selected_org)
        user.organisation_display = (
            user.organization_group.name
            if is_org_group_admin(user) and user.organization_group
            else ", ".join(user.organisation_data.values_list("name", flat=True)) or "—"
        )
        user.hide_organisation_information = is_super_or_58_admin(user)
        user.has_pending_invitation = UserInvitations.objects.filter(
            user=user,
            status__in=["SENT", "PENDING"],
        ).exists()

    return users
