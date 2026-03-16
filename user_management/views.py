from django.contrib import messages
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from django.template.loader import render_to_string
from django.views import View
import phonenumbers
from preference.models import OrganisationAccessCode, OrganisationData

from .forms import (
    AddWorkCodeForm,
    AppUserForm,
    CreateOrganisationForm,
    WorkCodeAssignForm,
    WorkGroupForm,
    UsersWorkGroupAssignForm,
)
from .decorators import group_required
from .models import AppUser, WorkGroup
from .utils import is_org_admin, is_super_or_58_admin


def get_allowed_orgs(user):
    if user.is_anonymous:
        return OrganisationData.objects.none()
    if is_super_or_58_admin(user):
        return OrganisationData.objects.all()
    if is_org_admin(user):
        org = user.organisation_data.order_by("name").first()
        if not org:
            return OrganisationData.objects.none()
        return OrganisationData.objects.filter(id=org.id)
    return OrganisationData.objects.none()


def has_org_access(user, organisation):
    if not organisation:
        return False
    return get_allowed_orgs(user).filter(id=organisation.id).exists()


def org_access_denied():
    return JsonResponse(
        {"ok": False, "error": "You do not have access to this organisation."},
        status=403,
    )


@group_required("user_management")
def user_management(request):
    user = request.user
    organizations = get_allowed_orgs(user).order_by("name")

    users = AppUser.objects.select_related("organisation_data").prefetch_related("work_groups").order_by("email")
    if is_org_admin(user):
        users = users.filter(organisation_data__in=organizations)

    work_codes = []
    work_groups = WorkGroup.objects.none()
    assigned_work_codes = []

    selected_org = None
    selected_org_id = None
    selected_org_name = None

    requested_org_id = request.GET.get("selected_org_id")
    if requested_org_id:
        selected_org = organizations.filter(id=requested_org_id).first()
        if selected_org:
            selected_org_id = str(selected_org.id)
            selected_org_name = selected_org.name

    if is_org_admin(user):
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
        "app_user_form": AppUserForm(work_groups_qs=work_groups),
        "assign_work_code_form": WorkCodeAssignForm(work_groups_qs=work_groups),
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
        AppUser.objects.select_related("organisation_data")
        .prefetch_related("work_groups")
        .order_by("email")
    )

    if is_org_admin(user):
        allowed_orgs = get_allowed_orgs(user)
        users = users.filter(organisation_data__in=allowed_orgs)

    if selected_org_id:
        organisation = (
            get_allowed_orgs(user).filter(id=selected_org_id).first()
        )
        if organisation:
            users = users.filter(organisation_data=organisation)
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
            organisation = form.save()
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
                        existing_code.expiry_date = form.cleaned_data["expiry_date"]
                        existing_code.requires_login = form.cleaned_data["requires_login"]
                        existing_code.save()
                        work_code = existing_code
                        msg = f'Work code "{work_code.code}" already exists but was deleted. It has been reactivated with the new details you provided.'
                    else:
                        work_code = form.save(commit=False)
                        work_code.organisation = organisation
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
        if not has_org_access(request.user, organisation):
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
        if not has_org_access(request.user, work_group.organisation):
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
                {"ok": False, "errors": {"organisation": ["Select an organisation first."]}},
                status=400,
            )
        if not has_org_access(request.user, organisation):
            return org_access_denied()
        work_groups_qs = WorkGroup.objects.filter(organisation=organisation).order_by("name")
        form = AppUserForm(request.POST, work_groups_qs=work_groups_qs)
        if form.is_valid():
            user = form.save(commit=False)
            user.organisation_data = organisation
            user.save()
            form.save_m2m()
            return JsonResponse({"ok": True, "org_id": organisation.id})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    
class EditAppUserView(View):
    
    def get(self, request, user_id):
        user = AppUser.objects.filter(id=user_id).select_related("organisation_data").prefetch_related("work_groups").first()
        if not user:
            return JsonResponse({"ok": False, "error": "User not found."}, status=404)
        
        if not has_org_access(request.user, user.organisation_data):
            return org_access_denied()
        
        organisation = user.organisation_data
        work_groups_qs = WorkGroup.objects.filter(organisation=organisation).order_by("name")
        phone_local = ""
        if user.phone_number:
            try:
                parsed = phonenumbers.parse(user.phone_number, None)
                phone_local = str(parsed.national_number)
            except phonenumbers.NumberParseException:
                phone_local = user.phone_number
        return JsonResponse({
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
                "work_group_ids": list(user.work_groups.values_list("id", flat=True)),
            },
            "work_groups": [
                {"id": work_group.id, "name": work_group.name} for work_group in work_groups_qs
            ],
        })

    def post(self, request, user_id):
        user = AppUser.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({"ok": False, "error": "User not found."}, status=404)
        
        if not has_org_access(request.user, user.organisation_data):
            return org_access_denied()
        
        organisation = user.organisation_data
        work_groups_qs = WorkGroup.objects.filter(organisation=organisation).order_by("name")
        form = AppUserForm(request.POST, instance=user, work_groups_qs=work_groups_qs)
        
        if form.is_valid():
            form.save()
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
        if not has_org_access(request.user, organisation):
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
        if work_group.users.exists():
            return JsonResponse(
                {"ok": False, "error": "This work group cannot be deleted because it has assigned users. Remove users first."},
                status=400,
            )
        name = work_group.name
        work_group.delete()
        messages.success(request, f'Work group "{name}" deleted successfully.')
        return JsonResponse({"ok": True, "org_id": organisation.id})
    
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
        if not has_org_access(request.user, organisation):
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
            users = AppUser.objects.filter(
                id__in=user_ids, organisation_data=organisation
            )
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
                {"ok": False, "errors": {"organisation": ["Select an organisation first."]}},
                status=400,
            )
        if not has_org_access(request.user, organisation):
            return org_access_denied()
        work_code = OrganisationAccessCode.objects.filter(
            id=work_code_id,
            organisation=organisation,
            is_deleted=False
        ).first()
        if not work_code:
            return JsonResponse(
                {"ok": False, "errors": {"work_code_id": ["Work code not found."]}},
                status=404,
            )
        form = AddWorkCodeForm(request.POST, instance=work_code)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {
                    "ok": True,
                    "org_id": organisation.id,
                    "work_code_id": work_code.id,
                }
            )

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
