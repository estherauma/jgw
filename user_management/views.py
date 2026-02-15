from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.views import View

from preference.models import OrganisationAccessCode, OrganisationData

from .forms import AddWorkCodeForm, CreateOrganisationForm



def user_management(request):
    organizations = OrganisationData.objects.order_by("name")

    users = [
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
        {"name": "Name Surname", "email": "name@email.com", "role": "Admin", "workgroup": "Accounts"},
    ]

    work_codes = []
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
        work_codes = (
            OrganisationAccessCode.objects.select_related("organisation")
            .filter(organisation=selected_org)
            .order_by("-created_at")
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
        "assigned_work_codes": assigned_work_codes,
        "selected_org_id": selected_org_id,
        "selected_org_name": selected_org_name,
        "org_details": org_details,
        "create_org_form": CreateOrganisationForm(),
        "add_work_code_form": AddWorkCodeForm(),
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
        org_id = request.GET.get("selected_org_id")
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

class EditOrganisationView(View):
    def post(self, request, organization_id):
        organisation = get_object_or_404(OrganisationData, pk=organization_id)
        form = CreateOrganisationForm(request.POST, instance=organisation)
        if form.is_valid():
            form.save()
            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
