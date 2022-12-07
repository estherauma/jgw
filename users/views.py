from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from users.tasks import send_email_notification

from .forms import CreateUserForm, InviteUserForm, LoginForm, UserMgtForm
from .models import User, UserInvitations
from .tasks import send_email_notification


@login_required
def list_users(request):
    users = User.objects.all()
    invitations = UserInvitations.objects.all()
    return render(request, "users/list_users.html", context={"users": users, "invitations": invitations})


@login_required
def logout_user(request):
    logout(request)
    return redirect("users:login_user")


def create_user_account(request):
    logout(request)
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            messages.info(request, "Your account was created and will be activated shortly.")
            return redirect("users:login_user")
        else:
            messages.error(request, "Error validating form!")
    return render(request, "users/create_user.html", context={"form": form})


def login_user(request):
    logout(request)
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard:inline")
            else:
                messages.error(request, "Can not log in with provided credentials!")
        else:
            messages.error(request, "Error validating form!")
    return render(request, "users/login.html", {"form": form})


@login_required
def manage_account(request, id):
    user = User.objects.get(id=id)
    form = UserMgtForm(instance=user)
    if request.method == "POST":
        form = UserMgtForm(data=request.POST, instance=user)
        if form.is_valid:
            form.save()
    return render(request, "users/manage_user.html", context={"form": form, "user": user})


@login_required
def activate_account(request, id):
    user = User.objects.get(id=id)
    subject = "Your account at JGWPandas."
    deactivation_message = (
        f"Hello\n, Your account at JGW Pandas has been deactivated.\n"
        f"\nPlease reach out to the administrator if this action was not initiated by you."
        f"\n\nJGWPandas"
    )
    activation_message = (
        f"Hello\n, Your account at JGW Pandas has been activated.\n"
        f"\n Please reach out to the administrator if this account was not created by you."
        f"\nJGWPandas"
    )
    if user.is_active:
        user.is_active = False
        user.save()
        messages.info(request, f"The user account: {user.email} was deactivated successfully.")
        send_email_notification.delay(
            subject=subject,
            message=deactivation_message,
            recipients=[user.email],
        )
    elif user.is_active == False:
        user.is_active = True
        user.save()
        messages.info(request, f"The user account: {user.email} was activated and will be notified shortly.")
        send_email_notification.delay(
            subject=subject,
            message=activation_message,
            recipients=[user.email],
        )
    return redirect("users:list_users")


@login_required
def invite_user(request):
    form = InviteUserForm()
    if request.method == "POST":
        form = InviteUserForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=True)
            email_address = form.cleaned_data.get("email")

            payload = {
                "exp": datetime.now(tz=timezone.utc) + timedelta(days=3),
                "invitation_id": invitation.id,
            }
            token = jwt.encode(payload=payload, key=settings.SECRET_KEY)

            messages.info(request, "The invitation email will be sent out shortly.")
            send_email_notification.delay(
                subject="Set up your account on JGWPandas",
                message=f"""
                    Please follow this link to set up your new account on JGW Pandas:
                    {reverse("users:accept_invite", args=(token,))}. 
                    Please note that this link expires in 3 days.
                """,
                recipients=[email_address],
            )
            return redirect("users:list_users")
        else:
            messages.error(request, "Error validating form!")
    return render(request, "users/invite_user.html", context={"form": form})
