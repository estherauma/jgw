from waffle.models import Flag

from .models import OrganisationRoleAssignment, OrganisationRolePermission
from preference.models import OrganisationData


def resolve_current_org(request, selected_org_id=None):
    if selected_org_id:
        return OrganisationData.objects.filter(id=selected_org_id).first()
    if not request or request.user.is_anonymous:
        return None
    orgs = request.user.organisation_data.all()
    if orgs.count() == 1:
        return orgs.first()
    return None


def user_has_role_flag(user, organisation, flag):
    if not user or user.is_anonymous or not organisation:
        return False
    role_ids = OrganisationRoleAssignment.objects.filter(
        user=user,
        organisation=organisation,
    ).values_list("role_id", flat=True)
    if not role_ids:
        return False
    return OrganisationRolePermission.objects.filter(
        role_id__in=role_ids,
        flag=flag,
    ).exists()


def is_flag_active(request, flag_name, organisation=None, selected_org_id=None):
    flag = Flag.objects.filter(name=flag_name).first()

    if not flag:
        return False
    if flag.everyone:
        return True
    if request and request.user.is_superuser:
        return True
    if not request or request.user.is_anonymous:
        return False
    if flag.is_active(request):
        return True
    if not organisation:
        organisation = resolve_current_org(request, selected_org_id=selected_org_id)

    if not organisation:
        return False
    return user_has_role_flag(request.user, organisation, flag)
