from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from preference.models import OrganisationAccessCode, OrganisationData

from .forms import (
    AddWorkCodeForm,
    AppUserForm,
    CreateOrganisationForm,
    WorkCodeAssignForm,
    WorkGroupForm,
)
from .models import AppUser, WorkGroup


def user_management(request):
    organizations = OrganisationData.objects.order_by("name")

    users = AppUser.objects.select_related("organisation_data").prefetch_related("work_groups").order_by("email")

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

    org_details = {
    }
    if selected_org:
        users = users.filter(organisation_data=selected_org)
        work_codes = (
            OrganisationAccessCode.objects.select_related("organisation")
            .filter(organisation=selected_org)
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


class CreateOrganisationView(View):
    def post(self, request):
        form = CreateOrganisationForm(request.POST)
        if form.is_valid():
            organisation = form.save()
            return JsonResponse({"ok": True, "org_id": organisation.id})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


class CreateWorkCodeView(View):
    def post(self, request):
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
            work_code = form.save(commit=False)
            work_code.organisation = organisation
            work_code.save()
            return JsonResponse(
                {
                    "ok": True,
                    "code": work_code.code,
                    "org_id": work_code.organisation_id,
                }
            )

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
        work_groups_qs = WorkGroup.objects.filter(organisation=organisation).order_by("name")
        form = AppUserForm(request.POST, work_groups_qs=work_groups_qs)
        if form.is_valid():
            user = form.save(commit=False)
            user.organisation_data = organisation
            user.save()
            form.save_m2m()
            return JsonResponse({"ok": True, "org_id": organisation.id})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)


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
        if not work_code_id:
            return JsonResponse(
                {"ok": False, "errors": {"work_code_id": ["Select a work code first."]}},
                status=400,
            )
        work_code = OrganisationAccessCode.objects.filter(
            id=work_code_id, organisation=organisation
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
