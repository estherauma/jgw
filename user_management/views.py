from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.views import View

from preference.models import OrganisationData

from .forms import CreateOrganisationForm



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

    unassigned_work_codes = [
        {"code": "HKEL5B5HD"},
        {"code": "HKEL5B5HD"},
        {"code": "HKEL5B5HD"},
    ]

    assigned_work_codes = [
        {"code": "TEST CODE", "group": "Devs"},
        {"code": "TEST CODE", "group": "Support"},
        {"code": "TEST CODE", "group": "Accounts"},
    ]

    org_details = {
        "name": "Test Organisation",
        "requires_auth": "YES",
        "code": "TESTORCODE",
        "prismic_repo": "TEST",
        "prismic_messaging_repo": "TEST",
        "created_by": "TEST",
        "created_at": "Feb 6, 2024, 12:57pm",
    }

    selected_org = "No organisation"
    first_org = organizations.first()
    if first_org:
        selected_org = f"{first_org.id} - {first_org.name}"

    context = {
        "organizations": organizations,
        "users": users,
        "unassigned_work_codes": unassigned_work_codes,
        "assigned_work_codes": assigned_work_codes,
        "selected_org": selected_org,
        "org_details": org_details,
        "create_org_form": CreateOrganisationForm(),
    }
    return render(request, "index.html", context=context)


class CreateOrganisationView(View):
    def post(self, request):
        form = CreateOrganisationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

class OrganizationDetailsView(View):
    def get(self,request,organization_id):
        organisation = get_object_or_404(OrganisationData, pk=organization_id)
        form = CreateOrganisationForm(instance=organisation)
        return render(request, "org-details.html", {"form": form, "organization": organisation})
        