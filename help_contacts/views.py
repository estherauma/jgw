from django.shortcuts import render


def help_contact_clicks(request):
    context = {}
    return render(
        request,
        "help_contacts/help_contacts.html", 
        context = context
    )