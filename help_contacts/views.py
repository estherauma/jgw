from django.shortcuts import render


def help_contact_clicks(request):
    phone_number_clicks_by_user = {
        "counts": [10, 20, 18],
        "labels": ["phonenumber one", "phonenumber two", "phonenumber three"]
    }
    
    email_clicks_by_user = {
        "counts": [40, 20, 77, 100, 11],
        "labels": ["email one", "email two", "email three", "email four", "email five"]
    }
    
    context = {
        "phone_number_clicks_by_user": phone_number_clicks_by_user,
        "email_clicks_by_user": email_clicks_by_user
    }
    return render(
        request,
        "help_contacts/help_contacts.html", 
        context = context
    )