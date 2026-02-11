from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
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

    selected_org = "Select organisation"

    org_details = {
        "name": "No organisation",
        "requires_auth": "N/A",
        "code": "N/A",
        "prismic_repo": "N/A",
        "prismic_messaging_repo": "N/A",
        "created_by": "N/A",
        "created_at": "N/A",
    }

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
