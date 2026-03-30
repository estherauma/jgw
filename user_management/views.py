from django.contrib import messages
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from django.template.loader import render_to_string
from django.views import View
import phonenumbers
import json
from preference.models import OrganisationAccessCode, OrganisationData

from .forms import (
    AddWorkCodeForm,
    AppUserForm,
    CreateOrganisationForm,
    DashboardUserForm,
    OrganisationRoleForm,
    WorkCodeAssignForm,
    WorkGroupForm,
    UsersWorkGroupAssignForm,
)
from .decorators import group_required
from .models import (
    OrganisationRole,
    OrganisationRoleAssignment,
    WorkGroup,
)
from .permissions import is_flag_active
from .roles import add_default_org_roles, apply_role_to_user
from .utils import is_58_admin, is_org_admin_or_staff, is_super_or_58_admin
from users.models import User


def get_allowed_orgs(user):
    if user.is_anonymous:
        return OrganisationData.objects.none()
    if is_super_or_58_admin(user):
        return OrganisationData.objects.all()
    if is_org_admin_or_staff(user):
        org = user.organisation_data.order_by("name").first()
        if not org:
            return OrganisationData.objects.none()
        return OrganisationData.objects.filter(id=org.id)
    return OrganisationData.objects.none()


def has_org_access(user, organisation, request=None, flag_name=None):
    if not organisation:
        return False
    if not get_allowed_orgs(user).filter(id=organisation.id).exists():
        return False
    if flag_name and request and is_org_admin_or_staff(user):
        return is_flag_active(request, flag_name, organisation=organisation)
    return True


def org_access_denied():
    return JsonResponse(
        {"ok": False, "error": "You do not have access to this organisation."},
        status=403,
    )


@group_required("user_management")
def user_management(request):
    user = request.user
    organizations = get_allowed_orgs(user).order_by("name")

    users = (
        User.objects.filter(is_deleted=False)
        .prefetch_related("organisation_data", "work_groups")
        .order_by("email")
        .distinct()
    )
    if is_org_admin_or_staff(user):
        users = users.filter(organisation_data__in=organizations)

    work_codes = []
    work_groups = WorkGroup.objects.none()
    assigned_work_codes = []
    roles = OrganisationRole.objects.none()

    selected_org = None
    selected_org_id = None
    selected_org_name = None

    requested_org_id = request.GET.get("selected_org_id")
    if requested_org_id:
        selected_org = organizations.filter(id=requested_org_id).first()
        if selected_org:
            selected_org_id = str(selected_org.id)
            selected_org_name = selected_org.name

    if is_org_admin_or_staff(user):
        selected_org = organizations.first()
        if selected_org:
            selected_org_id = str(selected_org.id)
            selected_org_name = selected_org.name

    org_details = {
    }
    if selected_org:
        users = users.filter(organisation_data=selected_org)
        work_codes = (
            OrganisationAccessCode.objects.select_related("organisation")
            .filter(organisation=selected_org, is_deleted=False)
            .order_by("-created_at")
        )
        work_groups = (
            WorkGroup.objects.select_related("organisation")
            .prefetch_related("access_codes")
            .filter(organisation=selected_org)
            .order_by("name")
        )
        roles = OrganisationRole.objects.filter(organisation=selected_org).prefetch_related(
            "role_permissions"
        ).order_by("name")
        org_details = {
            "name": selected_org.name,
            "code": selected_org.org_code,
            "created_by": "N/A",
            "created_at": selected_org.created_at,
        }

    context = {
        "organizations": organizations,
        "users": users,
        "work_codes": work_codes,
        "work_groups": work_groups,
        "assigned_work_codes": assigned_work_codes,
        "selected_org_id": selected_org_id,
        "selected_org_name": selected_org_name,
        "org_details": org_details,
        "create_org_form": CreateOrganisationForm(),
        "add_work_code_form": AddWorkCodeForm(),
        "work_group_form": WorkGroupForm(),
        "app_user_form": AppUserForm(work_groups_qs=work_groups, organisation=selected_org),
        "dashboard_user_form": DashboardUserForm(orgs_qs=organizations),
        "assign_work_code_form": WorkCodeAssignForm(work_groups_qs=work_groups),
        "roles": roles,
        "role_form": OrganisationRoleForm(organisation=selected_org, current_user=user),
    }
    return render(request, "index.html", context=context)


def search_organisations(request):
    user = request.user
    query = request.GET.get("q", "").strip()
    organisations = get_allowed_orgs(user).order_by("name")
    if query:
        organisations = organisations.filter(
            Q(name__icontains=query) | Q(org_code__icontains=query)
        )
    html = render_to_string(
        "organization-rows.html",
        {"organizations": organisations},
        request=request,
    )
    return JsonResponse({"ok": True, "html": html})


def search_users(request):
    user = request.user
    query = request.GET.get("q", "").strip()
    selected_org_id = request.GET.get("selected_org_id")
    users = (
        User.objects.filter(is_deleted=False)
        .prefetch_related("organisation_data", "work_groups")
        .order_by("email")
        .distinct()
    )

    if is_org_admin_or_staff(user):
        allowed_orgs = get_allowed_orgs(user)
        users = users.filter(organisation_data__in=allowed_orgs).distinct()

    if selected_org_id:
        organisation = (
            get_allowed_orgs(user).filter(id=selected_org_id).first()
        )
        if organisation:
            users = users.filter(organisation_data=organisation).distinct()
        else:
            users = users.none()

    if query:
        users = users.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )

    html = render_to_string(
        "user-rows.html",
        {"users": users, "selected_org_id": selected_org_id},
        request=request,
    )
    return JsonResponse({"ok": True, "html": html})


class CreateOrganisationView(View):
    def post(self, request):
        if not is_super_or_58_admin(request.user):
            return org_access_denied()
        form = CreateOrganisationForm(request.POST)
        if form.is_valid():
            organisation = form.save(commit=False)
            organisation.created_by = request.user
            organisation.updated_by = request.user
            organisation = form.save()
            add_default_org_roles(organisation)
            return JsonResponse({"ok": True, "org_id": organisation.id})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class CreateWorkCodeView(View):
    def post(self, request):
        if not is_super_or_58_admin(request.user):
            return org_access_denied()
        form = AddWorkCodeForm(request.POST)
        org_id = request.POST.get("selected_org_id")
        organisation = None
        if org_id:
            organisation = OrganisationData.objects.filter(id=org_id).first()
        if not organisation:
            return JsonResponse(
                {"ok": False, "errors": {"organisation": ["Select an organisation first."]}},
                status=400,
            )
        if form.is_valid():
            code_value = form.cleaned_data["code"].strip()
            try:
                with transaction.atomic():
                    existing_code = OrganisationAccessCode.objects.filter(
                        code__iexact=code_value
                        ).first()
                    if existing_code:
                        if existing_code.organisation != organisation:
                            return JsonResponse(
                                {"ok": False, "errors": {"code": ["Work code already exists for a different organisation."]}}, 
                                status=400)
                        if not existing_code.is_deleted:
                            return JsonResponse(
                                {"ok": False, "errors": {"code": ["Work code already exists."]}}, 
                                status=400)
         
                        existing_code.is_deleted = False
                        existing_code.deleted_at = None
                        existing_code.deleted_by = None
                        existing_code.updated_by = request.user
                        existing_code.expiry_date = form.cleaned_data["expiry_date"]
                        existing_code.requires_login = form.cleaned_data["requires_login"]
                        existing_code.save()
                        work_code = existing_code
                        msg = f'Work code "{work_code.code}" already exists but was deleted. It has been reactivated with the new details you provided.'
                    else:
                        work_code = form.save(commit=False)
                        work_code.organisation = organisation
                        work_code.created_by = request.user
                        work_code.updated_by = request.user
                        work_code.save()
                        msg = f'Work code "{work_code.code}" created successfully.'   
                    messages.success(request, msg)
                return JsonResponse(
                    {
                        "ok": True,
                        "code": work_code.code,
                        "org_id": work_code.organisation_id,
                    }
                )
            except IntegrityError:
                return JsonResponse({"ok": False,"errors": {"code": ["This code was just taken by another user or already exists. Please try a different one."]}}, 
                                        status=400)
                
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

class EditOrganisationView(View):
    def post(self, request, organisation_id):
        if not is_super_or_58_admin(request.user):
            return org_access_denied()
        organisation = OrganisationData.objects.filter(pk=organisation_id).first()
        if not organisation:
            return JsonResponse(
                {"ok": False, "error": "Organisation not found."},
                status=404,
            )
        form = CreateOrganisationForm(request.POST, instance=organisation)
        if form.is_valid():
            organisation = form.save(commit=False)
            organisation.updated_by = request.user
            form.save()
            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

class CreateWorkGroupView(View):
    def post(self, request):
        form = WorkGroupForm(request.POST)
        org_id = request.POST.get("selected_org_id")
        organisation = None
        if org_id:
            organisation = OrganisationData.objects.filter(id=org_id).first()
        if not organisation:
            return JsonResponse(
                {"ok": False, "errors": {"organisation": ["Select an organisation first."]}},
                status=400,
            )
        print("Organisation for new work group:", organisation)
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_create_workgroup",
        ):
            print("User does not have access to create work group in this organisation.")
            return org_access_denied()
        if form.is_valid():
            if WorkGroup.objects.filter(
                organisation=organisation, name__iexact=form.cleaned_data["name"]
            ).exists():
                return JsonResponse(
                    {"ok": False, "errors": {"name": ["Work group already exists."]}},
                    status=400,
                )
            work_group = form.save(commit=False)
            work_group.organisation = organisation
            work_group.created_by = request.user
            work_group.updated_by = request.user
            work_group.save()
            return JsonResponse(
                {
                    "ok": True,
                    "work_group_id": work_group.id,
                    "org_id": work_group.organisation_id,
                }
            )

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    
class EditWorkGroupView(View):
    def post(self, request, work_group_id):
        work_group = WorkGroup.objects.filter(pk=work_group_id).first()
        if not work_group:
            return JsonResponse(
                {"ok": False, "error": "Work group not found."},
                status=404,
            )
        if not has_org_access(
            request.user,
            work_group.organisation,
            request=request,
            flag_name="can_edit_workgroup",
        ):
            return org_access_denied()
        
        form = WorkGroupForm(request.POST, instance=work_group)
        if form.is_valid():
            if WorkGroup.objects.filter(
                organisation=work_group.organisation,
                name__iexact=form.cleaned_data["name"]
            ).exclude(pk=work_group_id).exists():
                return JsonResponse(
                    {"ok": False, "errors": {"name": ["Work group already exists."]}},
                    status=400,
                )
            work_group = form.save(commit=False)
            work_group.updated_by = request.user
            form.save()
            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class CreateAppUserView(View):
    def post(self, request):
        org_id = request.POST.get("selected_org_id")
        organisation = None
        if org_id:
            organisation = OrganisationData.objects.filter(id=org_id).first()

        if not organisation:
            return JsonResponse(
                {"ok": False, "error": "Select an organisation first."},
                status=400,
            )
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_create_appuser",
        ):
            return org_access_denied()
        work_groups_qs = WorkGroup.objects.filter(organisation=organisation).order_by("name")
        form = AppUserForm(
            request.POST,
            work_groups_qs=work_groups_qs,
            organisation=organisation,
        )
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.created_by = request.user
                    user.updated_by = request.user
                    password = form.cleaned_data.get("password")
                    role = form.cleaned_data.get("role")

                    if password:
                        user.set_password(password)
                    else:
                        user.set_unusable_password()

                    user.save()
                    form.save_m2m()
                    apply_role_to_user(user, organisation, role)
                    user.organisation_data.add(organisation)
            except Exception as e:
                return JsonResponse(
                    {"ok": False, "error": "Could not save user. Please try again."},
                    status=500,
                )
            return JsonResponse({"ok": True, "org_id": organisation.id if organisation else None})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class CreateDashboardUserView(View):
    def post(self, request):
        if not is_super_or_58_admin(request.user):
            return org_access_denied()
        form = DashboardUserForm(
            request.POST,
            orgs_qs=get_allowed_orgs(request.user),
        )
        if form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user
            user.updated_by = request.user
            password = form.cleaned_data.get("password")
            if password and is_58_admin(request.user) and user.id != request.user.id:
                return JsonResponse(
                    {
                        "ok": False,
                        "errors": {
                            "password": [
                                "You can only change your own password."
                            ]
                        },
                    },
                    status=400,
                )
            if password:
                user.set_password(password)
            else:
                user.set_unusable_password()
            user.is_active = form.cleaned_data.get("is_active", True)
            user.access_type = "dashboard"
            user.save()
            form.save_m2m()
            selected_groups = form.cleaned_data.get("groups")
            if selected_groups:
                user.groups.add(*selected_groups)
            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class EditDashboardUserView(View):
    def get(self, request, user_id):
        user = User.objects.prefetch_related(
            "organisation_data",
            "groups",
            "factories",
            "destinations",
            "user_languages",
            "excluded_origin_countries",
            "immigration_status",
        ).filter(id=user_id, access_type="dashboard").first()
        if not user:
            return JsonResponse({"ok": False, "error": "User not found."}, status=404)
        if not is_super_or_58_admin(request.user):
            return org_access_denied()

        return JsonResponse(
            {
                "ok": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                    "scheme_id": user.scheme_id,
                    "start_date": user.start_date.isoformat()
                    if user.start_date
                    else "",
                    "end_date": user.end_date.isoformat() if user.end_date else "",
                    "groups": list(user.groups.values_list("id", flat=True)),
                    "organisation_data": list(
                        user.organisation_data.values_list("id", flat=True)
                    ),
                    "factories": list(user.factories.values_list("id", flat=True)),
                    "destinations": list(user.destinations.values_list("id", flat=True)),
                    "user_languages": list(
                        user.user_languages.values_list("id", flat=True)
                    ),
                    "excluded_origin_countries": list(
                        user.excluded_origin_countries.values_list("id", flat=True)
                    ),
                    "immigration_status": list(
                        user.immigration_status.values_list("id", flat=True)
                    ),
                },
            }
        )

    def post(self, request, user_id):
        user = User.objects.filter(id=user_id, access_type="dashboard").first()
        if not user:
            return JsonResponse({"ok": False, "error": "User not found."}, status=404)
        if not is_super_or_58_admin(request.user):
            return org_access_denied()

        form = DashboardUserForm(
            request.POST,
            instance=user,
            orgs_qs=get_allowed_orgs(request.user),
        )
        if form.is_valid():
            user = form.save(commit=False)
            user.updated_by = request.user
            password = form.cleaned_data.get("password")
            if password:
                user.set_password(password)
            user.is_active = form.cleaned_data.get("is_active", True)
            user.save()
            form.save_m2m()
            selected_groups = form.cleaned_data.get("groups")
            if selected_groups is not None:
                user.groups.set(selected_groups)
            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class EditAppUserView(View):
    
    def get(self, request, user_id):
        user = (
            User.objects.filter(id=user_id)
            .prefetch_related("organisation_data", "work_groups", "groups")
            .first()
        )
        if not user:
            return JsonResponse({"ok": False, "error": "User not found."}, status=404)

        allowed_orgs = get_allowed_orgs(request.user)
        organisation = user.organisation_data.filter(id__in=allowed_orgs).first()
        if not organisation:
            return org_access_denied()
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_edit_appuser",
        ):
            return org_access_denied()

        work_groups_qs = WorkGroup.objects.filter(organisation=organisation).order_by(
            "name"
        )
        roles_qs = OrganisationRole.objects.filter(organisation=organisation).order_by("name")
        phone_local = ""
        if user.phone_number:
            try:
                parsed = phonenumbers.parse(user.phone_number, None)
                phone_local = str(parsed.national_number)
            except phonenumbers.NumberParseException:
                phone_local = user.phone_number
        role_assignment = OrganisationRoleAssignment.objects.filter(
            user=user,
            organisation=organisation,
        ).select_related("role").first()
        role_id = role_assignment.role_id if role_assignment else ""
        if not role_id:
            fallback_role = OrganisationRole.objects.filter(
                organisation=organisation,
                grants_dashboard_access=user.access_type == "dashboard",
            ).order_by("name").first()
            role_id = fallback_role.id if fallback_role else ""
        return JsonResponse(
            {
                "ok": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                    "phone_country_iso": user.phone_country_iso,
                    "phone_local": phone_local,
                    "organisation_name": organisation.name,
                    "work_group_ids": list(
                        user.work_groups.values_list("id", flat=True)
                    ),
                    "role_id": role_id,
                },
                "work_groups": [
                    {"id": work_group.id, "name": work_group.name}
                    for work_group in work_groups_qs
                ],
                "roles": [
                    {"id": role.id, "name": role.name}
                    for role in roles_qs
                ],
            }
        )

    def post(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({"ok": False, "error": "User not found."}, status=404)

        allowed_orgs = get_allowed_orgs(request.user)
        organisation = user.organisation_data.filter(id__in=allowed_orgs).first()
        if not organisation:
            return org_access_denied()
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_edit_appuser",
        ):
            return org_access_denied()

        work_groups_qs = WorkGroup.objects.filter(organisation=organisation).order_by(
            "name"
        )
        form = AppUserForm(
            request.POST,
            instance=user,
            work_groups_qs=work_groups_qs,
            organisation=organisation,
        )
        
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get("role")
            if not role:
                return JsonResponse(
                    {"ok": False, "errors": {"role": ["Role is required."]}},
                    status=400,
                )
            password = form.cleaned_data.get("password")
            if password:
                is_worker = not role.grants_dashboard_access
                is_self = user.id == request.user.id
                if not (is_worker or is_self):
                    return JsonResponse(
                        {
                            "ok": False,
                            "errors": {
                                "password": [
                                    "You can only change passwords for app users or your own account."
                                ]
                            },
                        },
                        status=400,
                    )
            if password:
                user.set_password(password)
            user.updated_by = request.user
            user.save()
            form.save_m2m()
            apply_role_to_user(user, organisation, role)
            return JsonResponse({"ok": True, "org_id": organisation.id})
        errors = {field: [e for e in errs] for field, errs in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)


class AssignWorkCodeView(View):
    def post(self, request):
        org_id = request.POST.get("selected_org_id")
        work_code_id = request.POST.get("work_code_id")
        organisation = None
        if org_id:
            organisation = OrganisationData.objects.filter(id=org_id).first()
        if not organisation:
            return JsonResponse(
                {"ok": False, "errors": {"organisation": ["Select an organisation first."]}},
                status=400,
            )
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_assign_work_code",
        ):
            return org_access_denied()
        if not work_code_id:
            return JsonResponse(
                {"ok": False, "errors": {"work_code_id": ["Select a work code first."]}},
                status=400,
            )
        work_code = OrganisationAccessCode.objects.filter(
            id=work_code_id, organisation=organisation, is_deleted=False
        ).first()
        if not work_code:
            return JsonResponse(
                {"ok": False, "errors": {"work_code_id": ["Work code not found."]}},
                status=400,
            )
        work_groups_qs = WorkGroup.objects.filter(organisation=organisation).order_by("name")
        form = WorkCodeAssignForm(request.POST, work_groups_qs=work_groups_qs)
        if form.is_valid():
            work_groups = form.cleaned_data["work_groups"]
            work_code.work_groups.set(work_groups)
            return JsonResponse(
                {
                    "ok": True,
                    "org_id": organisation.id,
                    "work_code_id": work_code.id,
                }
            )

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class DeleteWorkGroupView(View):
    def post(self, request, work_group_id):
        allowed_orgs = get_allowed_orgs(request.user)
        work_group = WorkGroup.objects.filter(id=work_group_id, organisation__in=allowed_orgs).first()
        if not work_group:
            return JsonResponse({"ok": False, "error": "Work group not found."}, status=404)
        organisation = work_group.organisation
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_delete_workgroup",
        ):
            return org_access_denied()
        if work_group.users.exists():
            return JsonResponse(
                {"ok": False, "error": "This work group cannot be deleted because it has assigned users. Remove users first."},
                status=400,
            )
        name = work_group.name
        work_group.delete()
        messages.success(request, f'Work group "{name}" deleted successfully.')
        return JsonResponse({"ok": True, "org_id": organisation.id})


class CreateOrganisationRoleView(View):
    def post(self, request):
        org_id = request.POST.get("selected_org_id")
        organisation = None
        if org_id:
            organisation = OrganisationData.objects.filter(id=org_id).first()
        if not organisation:
            return JsonResponse(
                {"ok": False, "errors": {"organisation": ["Select an organisation first."]}},
                status=400,
            )
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_create_role",
        ):
            return org_access_denied()
        form = OrganisationRoleForm(request.POST, organisation=organisation)
        if form.is_valid():
            role = form.save()
            return JsonResponse({"ok": True, "role_id": role.id})
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class EditOrganisationRoleView(View):
    def get(self, request, role_id):
        role = OrganisationRole.objects.filter(
            id=role_id, organisation__in=get_allowed_orgs(request.user)
        ).first()
        if not role:
            return JsonResponse({"ok": False, "error": "Role not found."}, status=404)
        if not has_org_access(
            request.user,
            role.organisation,
            request=request,
            flag_name="can_edit_role",
        ):
            return org_access_denied()
        permission_ids = list(role.role_permissions.values_list("flag_id", flat=True))
        return JsonResponse(
            {
                "ok": True,
                "role": {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "grants_dashboard_access": role.grants_dashboard_access,
                    "permission_ids": permission_ids,
                    "is_system": role.is_system,
                },
            }
        )

    def post(self, request, role_id):
        role = OrganisationRole.objects.filter(
            id=role_id, organisation__in=get_allowed_orgs(request.user)
        ).first()
        if not role:
            return JsonResponse({"ok": False, "error": "Role not found."}, status=404)
        if not has_org_access(
            request.user,
            role.organisation,
            request=request,
            flag_name="can_edit_role",
        ):
            return org_access_denied()
        form = OrganisationRoleForm(
            request.POST, instance=role, organisation=role.organisation
        )
        if form.is_valid():
            form.save()
            return JsonResponse({"ok": True, "role_id": role.id})
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class DeleteOrganisationRoleView(View):
    def post(self, request, role_id):
        role = OrganisationRole.objects.filter(
            id=role_id, organisation__in=get_allowed_orgs(request.user)
        ).first()
        if not role:
            return JsonResponse({"ok": False, "error": "Role not found."}, status=404)
        if not has_org_access(
            request.user,
            role.organisation,
            request=request,
            flag_name="can_delete_role",
        ):
            return org_access_denied()
        if role.is_system:
            return JsonResponse(
                {"ok": False, "error": "System roles cannot be deleted."},
                status=400,
            )
        if role.assignments.exists():
            return JsonResponse(
                {
                    "ok": False,
                    "error": "Remove users from this role before deleting it.",
                },
                status=400,
            )
        role.delete()
        return JsonResponse({"ok": True})
    
class AssignUsersToWorkGroupsView(View):
    def post(self, request):
        org_id = request.POST.get("selected_org_id")
        user_ids_raw = request.POST.get("user_ids", "")
        organisation = None
        if org_id:
            organisation = OrganisationData.objects.filter(id=org_id).first()
        if not organisation:
            return JsonResponse(
                {"ok": False, "error": "Select an organisation first."},
                status=400,
            )
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_assign_users_to_workgroups",
        ):
            return org_access_denied()

        user_ids = [
            value
            for value in user_ids_raw.split(",")
            if value.strip()
        ]
        if not user_ids:
            return JsonResponse(
                {"ok": False, "error": "Select at least one user."},
                status=400,
            )

        work_groups_qs = WorkGroup.objects.filter(organisation=organisation)
        form = UsersWorkGroupAssignForm(request.POST, work_groups_qs=work_groups_qs)
        if form.is_valid():
            work_groups = list(form.cleaned_data["work_groups"])
            users = User.objects.filter(
                id__in=user_ids, organisation_data=organisation, access_type="app"
            ).distinct()
            if not users.exists():
                return JsonResponse(
                    {"ok": False, "error": "No matching users found."},
                    status=400,
                )
            for user in users:
                user.work_groups.add(*work_groups)
            return JsonResponse(
                {"ok": True, "org_id": organisation.id, "user_count": users.count()}
            )

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class DeleteWorkCodeView(View):
    def post(self, request, work_code_id):
        if not is_super_or_58_admin(request.user):
            return org_access_denied()
        allowed_orgs = get_allowed_orgs(request.user)
        work_code = OrganisationAccessCode.objects.filter(
            id=work_code_id,
            organisation__in=allowed_orgs,
            is_deleted=False
        ).first()

        if not work_code:
            return JsonResponse(
                {"ok": False, "error": "Work code not found."},
                status=404,
            )
        if not has_org_access(
            request.user,
            work_code.organisation,
            request=request,
            flag_name="can_delete_work_code",
        ):
            return org_access_denied()

        if work_code.work_groups.exists():
            return JsonResponse(
                {
                    "ok": False, 
                    "error": f"Cannot delete '{work_code.code}' because it is assigned to work groups. Remove it from the work groups first."
                },
                status=400,
            )

        code = work_code.code
        
        work_code.soft_delete(request.user)
        
        messages.success(request, f'Work code "{code}" deleted successfully.')
        return JsonResponse({"ok": True})
    
class EditWorkCodeView(View):
    def post(self, request, work_code_id):
        org_id = request.POST.get("selected_org_id")
        organisation = None
        if org_id:
            organisation = OrganisationData.objects.filter(id=org_id).first()
        if not organisation:
            return JsonResponse(
                {"ok": False, "error": "Select an organisation first."},
                status=400,
            )
        if not has_org_access(
            request.user,
            organisation,
            request=request,
            flag_name="can_edit_work_code",
        ):
            return org_access_denied()
        work_code = OrganisationAccessCode.objects.filter(
            id=work_code_id,
            organisation=organisation,
            is_deleted=False
        ).first()
        if not work_code:
            return JsonResponse(
                {"ok": False, "error": "Work code not found."},
                status=404,
            )
        form = AddWorkCodeForm(request.POST, instance=work_code)
        if form.is_valid():
            work_code = form.save(commit=False)
            work_code.updated_by = request.user
            form.save()
            return JsonResponse(
                {
                    "ok": True,
                    "org_id": organisation.id,
                    "work_code_id": work_code.id,
                }
            )

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class DeleteUserView(View):
    def post(self, request):
        current_user = request.user
        try:
            data = json.loads(request.body)
            ids_param = data.get('ids', '')
            
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse(
                {"ok": False, "error": "Invalid JSON data."},
                status=400,
            )
              
        raw_ids = [uid.strip() for uid in ids_param.split(',') if uid.strip()]
        
        if not raw_ids:
            return JsonResponse({"ok": False, "error": "No User selected."}, status=400)
        
        if not (is_super_or_58_admin(current_user) or is_org_admin_or_staff(current_user)):
            return JsonResponse({"ok": False, "error": "Permission denied."}, status=403)

        target_users = list(User.objects.filter(id__in=raw_ids).prefetch_related('organisation_data'))
        
        users_to_delete = []
        failed_emails = []
            
        for target_user in target_users:
            if target_user.id == current_user.id:
                continue
            
            can_delete = False

            if current_user.is_superuser:
                can_delete = True
                
            elif is_58_admin(current_user):
                if getattr(target_user, 'created_by_id', None) == current_user.id:
                    can_delete = True
                else:
                    identifier = target_user.email or f"ID {target_user.id}"
                    failed_emails.append(str(identifier))
                    
            elif is_org_admin_or_staff(current_user):
                target_org = target_user.organisation_data.first()
                if target_org and has_org_access(current_user, target_org):
                    can_delete = True
                else:
                    identifier = target_user.email or f"ID {target_user.id}"
                    failed_emails.append(str(identifier))

            if can_delete:
                users_to_delete.append(target_user)

        if failed_emails:
            emails_list = ", ".join(failed_emails)
            
            if is_58_admin(current_user):
                error_prefix = "58 Admins can only delete users they created. Failed at: "
            elif is_org_admin_or_staff(current_user):
                error_prefix = "Org Admins can only delete users within their organisation. Failed at: "
            else:
                error_prefix = "Permission denied for: "
                
            return JsonResponse({
                "ok": False, 
                "error": f"{error_prefix}{emails_list}."
            }, status=403)

        if users_to_delete:
            deleted_emails = []
            with transaction.atomic():
                for user in users_to_delete:
                    user.soft_delete(deleted_by=current_user)
                    if user.email:
                        deleted_emails.append(str(user.email))
                        
            email_string = ', '.join(filter(None, deleted_emails))
                    
            if email_string:
                messages.success(request, f"Successfully deleted: {email_string}")
            else:
                count = len(users_to_delete)
                messages.success(request, f"Successfully deleted {count} user(s).")
                
            return JsonResponse({"ok": True})
                
        return JsonResponse({"ok": False, "error": "Permission denied."}, status=403)