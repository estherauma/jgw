from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from users.tasks import send_email_notification

from .forms import CreateUserForm, InviteUserForm, LoginForm, SetPasswordForm, UserMgtForm
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
            email_address = form.cleaned_data.get("email")
            account_exists = User.objects.filter(email=email_address).exists()
            if account_exists:
                messages.error(request, "An account with this email address already exists!")
                return render(request, "users/invite_user.html", context={"form": form})

            invitation = form.save(commit=True)
            payload = {
                "exp": datetime.now(tz=timezone.utc) + timedelta(days=3),
                "invitation_id": invitation.id,
            }
            token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")
            send_email_notification.delay(
                subject="Set up your account on JGWPandas",
                message=f"""
                Please follow this link to set up your new account on JGW Pandas:
                https://jgwpandas.herokuapp.com{reverse("users:handle_invite", args=(token,))}
                \nPlease note that this link expires in 3 days.
                """,
                recipients=[email_address],
            )
            messages.info(request, "The invitation email will be sent out shortly.")
            return redirect("users:list_users")
        else:
            messages.error(request, "Error validating form!")
    return render(request, "users/invite_user.html", context={"form": form})


def handle_invite(request, token):
    logout(request)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        instance = UserInvitations.objects.get(id=payload.get("invitation_id"))
        invitation = UserInvitations.objects.values("email", "role", "scheme", "factory", "organisation").get(
            id=payload.get("invitation_id")
        )
        invitation["scheme_id"] = invitation.pop("scheme")
        invitation["factory_id"] = invitation.pop("factory")
        new_account = User.objects.create(**invitation, password='')
        instance.status = "ACCEPTED"
        instance.save()
        payload = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "user_id": new_account.id,
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY)
        return redirect(reverse("users:set_password", args=(token,)))
    except jwt.ExpiredSignatureError:
        messages.error(request, "This link is expired!")
    except UserInvitations.DoesNotExist:
        messages.error(request, "Invitation not found!")
    return render(request, "users/handle_invite.html")


def set_password(request, token):
    logout(request)
    form = SetPasswordForm()
    if request.method == "POST":
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_account = User.objects.get(id=payload.get("user_id"))
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get("password")
                user_account.set_password(password)
                user_account.is_active = True
                user_account.save()
                return redirect("users:login_user")
            else:
                messages.error(request, "Error validating form!")
        except jwt.ExpiredSignatureError:
            messages.error(request, "This link is expired!")
        except User.DoesNotExist:
            messages.error(request, "User account not found!")
    return render(request, "users/set_password.html", {"form": form})
