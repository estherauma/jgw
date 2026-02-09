from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime


def user_management(request):
    organizations = [
        {
            "name": "Organisation Name",
            "code": "XXXXXX",
            "required_login": "YES",
            "prismic_repo": "Text Example",
        },
        {
            "name": "Test Organisation",
            "code": "XXXXXX",
            "required_login": "YES",
            "prismic_repo": "Text Example",
        },
        {
            "name": "Organisation Name",
            "code": "XXXXXX",
            "required_login": "YES",
            "prismic_repo": "Text Example",
        },
        {
            "name": "Organisation Name",
            "code": "XXXXXX",
            "required_login": "YES",
            "prismic_repo": "Text Example",
        },
        {
            "name": "Organisation Name",
            "code": "XXXXXX",
            "required_login": "YES",
            "prismic_repo": "Text Example",
        },
        {
            "name": "Organisation Name",
            "code": "XXXXXX",
            "required_login": "YES",
            "prismic_repo": "Text Example",
        },
    ]

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

    context = {
        "organizations": organizations,
        "users": users,
        "unassigned_work_codes": unassigned_work_codes,
        "assigned_work_codes": assigned_work_codes,
        "selected_org": "84 - Test Organisation",
        "org_details": org_details,
    }
    return render(request, "index.html", context=context)
