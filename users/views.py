from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponseRedirect

from users.tasks import send_email_notification

from .forms import (
    ChangeEmailForm,
    CreateUserForm,
    InviteUserForm,
    LoginForm,
    RequestPasswordResetForm,
    SetPasswordForm,
    UpdateUserProfileForm,
    UserMgtForm,
)
from .models import User, UserInvitations


@login_required
def list_users(request):
    users = User.objects.all()
    return render(request, "users/list_users.html", context={"users": users})


@login_required
def list_invitations(request):
    invitations = UserInvitations.objects.all()
    return render(request, template_name="users/list_invitations.html", context={"invitations": invitations})


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
    return render(request, "users/sign_up.html", context={"form": form})


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
    return render(request, "users/sign_in.html", {"form": form})


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
            subject=subject, message=deactivation_message, recipients=[user.email], attachment_path=None
        )
    elif user.is_active == False:
        user.is_active = True
        user.save()
        messages.info(request, f"The user account: {user.email} was activated and will be notified shortly.")
        send_email_notification.delay(
            subject=subject, message=activation_message, recipients=[user.email], attachment_path=None
        )
    return redirect("users:list_users")


def generate_token(payload_data=None, days_to_expiry=1):
    """Returns a jwt token that expires in `days_to_expiry` days

    Args:
        payload_data: any extra data apart from the exp claimset to encode in the token.
        days_to_expiry: number of days after creation token expires.

    Returns:
        token: jwt token string encoded with settings.SECRET_KEY
    """
    payload = {"exp": datetime.now(tz=timezone.utc) + timedelta(days=days_to_expiry)}
    if payload_data:
        payload.update(payload_data)
    token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")
    return token


@login_required
def invite_user(request):
    form = InviteUserForm()
    if request.method == "POST":
        form = InviteUserForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data.get("email")
            invite = form.save(commit=True)
            token = generate_token(payload_data={"invite_id": invite.id}, days_to_expiry=3)
            send_email_notification.delay(
                subject="Set up your account on JGWPandas",
                message=f"""
                Please follow this link to set up your new account on JGW Pandas:
                https://jgwpandas.herokuapp.com{reverse("users:verify_invite", args=(token,))}
                \nPlease note that this link expires in 3 days.
                """,
                recipients=[email_address],
                attachment_path=None,
            )
            messages.info(request, "The invitation email will be sent out shortly.")
            return redirect("users:list_users")
        else:
            messages.error(request, "Error validating form!")
    return render(request, "users/invite_user.html", context={"form": form})


def verify_invite(request, token):
    logout(request)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        invite = UserInvitations.objects.get(id=payload.get("invite_id"))
        invite.status = "ACCEPTED"
        invite.save()
        token = generate_token(payload_data={"invite_id": invite.id}, days_to_expiry=1)
        return redirect(reverse("users:set_password", args=(token,)))
    except jwt.ExpiredSignatureError:
        messages.error(request, "This link is expired!")
    except UserInvitations.DoesNotExist:
        messages.error(request, "Invitation not found!")
    return render(request, "users/handle_invite.html")


@login_required
def profile(request):
    profile = User.objects.get(id=request.user.id)

    if request.method == "POST":
        form = UpdateUserProfileForm(request.POST or None, instance=request.user)
        if not request.GET.get('tab') or request.GET.get('tab') == 'profile':
            if form.is_valid():
                profile.first_name = form.cleaned_data.get("first_name")
                profile.last_name = form.cleaned_data.get("last_name")
                profile.email = form.cleaned_data.get("email")
                profile.receive_marketing_emails = form.cleaned_data.get("receive_marketing_emails")
                profile.save()
                messages.info(request, "Profile updated successfully!")
            else:
                messages.error(request, "Error validating form!")
                
        if request.GET.get('tab') == 'password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                if request.user.check_password(old_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, 'Password successfully changed!')
                    logout(request)
                    return redirect("users:login_user")
                else:
                    messages.error(request, 'Old password does not match!')
            else:
                messages.error(request, 'New password and confirm password do not match!')

    form = UpdateUserProfileForm(initial={
        "first_name": profile.first_name, 
        "last_name": profile.last_name,
        "email": profile.email,
        'receive_marketing_emails': profile.receive_marketing_emails,
    })
    context = {"profile": profile, 'form': form}
    return render(request, template_name="users/profile.html", context=context)


def request_password_reset(request):
    logout(request)
    form = RequestPasswordResetForm()
    if request.method == "POST":
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data.get("email")
            try:
                user = User.objects.get(email=email_address)
                token = generate_token(payload_data={"user_id": user.id}, days_to_expiry=1)
                send_email_notification.delay(
                    subject="Reset your password on JGWPandas",
                    message=f"""
                    Follow this link to reset the password for your account on JGW Pandas:
                    \n https://jgwpandas.herokuapp.com{reverse("users:set_password", args=(token,))}
                    \n This link expires in 1 day.
                    """,
                    recipients=[email_address],
                    attachment_path=None,
                )
                success_text = f"""
                    An email has been sent to {email_address}.
                    Please check for an email from JGWPandas and click on the included link to reset your password.
                    """
                return render(
                    request, template_name="users/email_sent.html", context={"success_text": success_text}
                )
            except User.DoesNotExist:
                form.full_clean()
                messages.error(request, "No user account matches this email address!")
    return render(request, template_name="users/request_password_reset.html", context={"form": form})


def set_password(request, token):
    logout(request)
    form = SetPasswordForm()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id, invite_id = payload.get("user_id"), payload.get("invite_id")
        if user_id is None and invite_id is None:
            messages.error(request, "Invalid token!")
            return redirect("users:login_user")
        if request.method == "POST":
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get("confirm_password")
                if user_id:
                    user = User.objects.get(id=user_id)
                    user.set_password(password)
                    user.save()
                elif invite_id:
                    invite = UserInvitations.objects.values(
                        "email", "role", "scheme", "factory", "organisation"
                    ).get(id=invite_id)
                    invite["scheme_id"], invite["factory_id"] = invite.pop("scheme"), invite.pop("factory")
                    User.objects.create_user(**invite, password=password, is_active=True)
                return redirect("users:login_user")
            else:
                messages.error(request, "Error validating form!")
    except jwt.ExpiredSignatureError:
        messages.error(request, "This link is expired!")
    except User.DoesNotExist:
        messages.error(request, "User account not found!")
    return render(request, "users/set_password.html", {"form": form})


@login_required
def change_email_address(request):
    user = request.user
    old_email = user.email
    form = ChangeEmailForm()
    if request.method == "POST":
        logout(request)
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data.get("new_email")
            if new_email == old_email:
                messages.error(request, "New email must be different from current email!")
            elif User.objects.filter(email=new_email):
                messages.error(request, "A user with this email address already exists!")
            else:
                token = generate_token(
                    payload_data={"user_id": user.id, "new_email": new_email}, days_to_expiry=1
                )
                send_email_notification.delay(
                    subject="Verify your email",
                    message=f"""
                    \n Click this link to verify this email for your account on JGW Pandas:
                    \n https://jgwpandas.herokuapp.com{reverse("users:verify_email", args=(token,))}
                    \n This link expires in 1 day.
                    \n Reach out to your administrator if you didn't initiate this action.
                    """,
                    recipients=[new_email],
                    attachment_path=None,
                )
                success_text = f"""
                    An email has been sent to {new_email}.
                    Please check for an email from JGWPandas and click on the included link to verify the change in email address.
                    """
                return render(
                    request, template_name="users/email_sent.html", context={"success_text": success_text}
                )
        else:
            messages.error(request, "Error validating form!")
    return render(request, template_name="users/change_email.html", context={"form": form})


def verify_email_change(request, token):
    logout(request)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id, new_email = payload.get("user_id"), payload.get("new_email")
        if user_id and new_email:
            user = User.objects.get(id=user_id)
            user.email = new_email
            user.save()
        else:
            messages.error(request, "Invalid token!")
    except jwt.ExpiredSignatureError:
        messages.error(request, "This link is expired!")
    except User.DoesNotExist:
        messages.error(request, "User account not found!")
    return redirect("users:login_user")
