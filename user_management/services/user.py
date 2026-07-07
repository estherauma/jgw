from django.core.paginator import Paginator
from django.db.models import Q

from users.models import User

from user_management.services.organization import OrganizationService
from user_management.roles import add_default_org_roles, apply_role_to_user
from user_management.utils import (
    get_active_role,
    get_group_names,
    is_org_admin_or_staff,
    is_org_group_admin,
    is_super_or_58_admin,
)

USER_GROUP_FILTER_OPTIONS = [
    {"value": "58_admin", "label": "Fifty Eight Administrator"},
    {"value": "org_group_admin", "label": "Organisation Group Administrator"},
    {"value": "org_admin", "label": "Organisation Administrator"},
    {"value": "org_staff", "label": "Organisation Staff"},
    {"value": "worker", "label": "Worker"},
]


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


def filter_users_query(queryset, query=""):
    query = (query or "").strip()
    if not query:
        return queryset
    return queryset.filter(
        Q(first_name__icontains=query)
        | Q(last_name__icontains=query)
        | Q(email__icontains=query)
    )


def filter_users_status(queryset, status=""):
    if not status:
        return queryset
    if status == "active":
        return queryset.filter(is_active=True)
    if status == "inactive":
        return queryset.filter(is_active=False)
    return queryset


def filter_users_role(queryset, role="", selected_org=None):
    if not role:
        return queryset
    if selected_org:
        if not str(role).isdigit():
            return queryset.filter(groups__name=role).distinct()

        role_obj = selected_org.roles.filter(id=role).first()
        if not role_obj:
            return queryset.none()

        role_filter = Q(
            org_roles__organisation=selected_org,
            org_roles__role_id=role,
        )
        if role_obj.is_system and role_obj.name == "Administrator":
            role_filter |= Q(groups__name="org_admin")
        elif role_obj.is_system and role_obj.name == "Worker":
            role_filter |= Q(groups__name="worker")

        return queryset.filter(role_filter).distinct()
    return queryset.filter(groups__name=role).distinct()


def filter_users_work_group(queryset, work_group_id=""):
    if not work_group_id:
        return queryset
    return queryset.filter(work_groups__id=work_group_id).distinct()


def decorate_users_for_listing(users, selected_org=None):
    users = list(users)
    if not users:
        return users

    for user in users:
        user.role_display = get_user_role_display(user, selected_org=selected_org)
        user.organisation_display = (
            user.organization_group.name
            if is_org_group_admin(user) and user.organization_group
            else ", ".join(org.name for org in user.organisation_data.all()) or "—"
        )
        user.hide_organisation_information = is_super_or_58_admin(user)

    return users


def get_paginated_users_context(
    current_user,
    selected_org=None,
    query="",
    page_number=None,
    filters=None,
):
    filters = filters or {}
    organisation_id = (filters.get("organisation_id") or "").strip()
    status = (filters.get("status") or "").strip()
    role = (filters.get("role") or "").strip()
    work_group_id = (filters.get("work_group_id") or "").strip()

    queryset = (
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

    allowed_orgs = None
    if is_org_admin_or_staff(current_user):
        allowed_orgs = OrganizationService.get_allowed_orgs(current_user)
        queryset = queryset.filter(organisation_data__in=allowed_orgs).distinct()

    if selected_org:
        queryset = queryset.filter(organisation_data=selected_org)
    elif organisation_id:
        if allowed_orgs is None:
            allowed_orgs = OrganizationService.get_allowed_orgs(current_user)
        queryset = queryset.filter(
            organisation_data__in=allowed_orgs.filter(id=organisation_id)
        ).distinct()

    queryset = filter_users_status(queryset, status=status)
    queryset = filter_users_role(queryset, role=role, selected_org=selected_org)
    queryset = filter_users_work_group(queryset, work_group_id=work_group_id)
    queryset = filter_users_query(queryset, query)
    paginator = Paginator(queryset, 20)
    users_page = paginator.get_page(page_number)
    users = decorate_users_for_listing(users_page.object_list, selected_org=selected_org)

    return {
        "users": users,
        "users_page": users_page,
        "users_pagination_context": {
            "page_obj": users_page,
            "page_numbers": list(users_page.paginator.get_elided_page_range(users_page.number)),
            "item_label": "users",
            "nav_label": "Users pagination",
            "page_link_attr": "data-users-page-link",
        },
        "row_start_index": users_page.start_index() if users_page.object_list else 0,
    }
