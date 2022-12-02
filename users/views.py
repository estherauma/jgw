from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from users.tasks import send_email_notification

from .forms import CreateUserForm, InviteUserForm, LoginForm, UserMgtForm
from .models import User


@login_required()
def list_users(request):
    queryset = User.objects.all()
    return render(request, "users/list.html", context={"users": queryset})


@login_required()
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
    return render(request, "users/create.html", context={"form": form})


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


@login_required()
def manage_account(request, id):
    user = User.objects.get(id=id)
    form = UserMgtForm(instance=user)
    if request.method == "POST":
        form = UserMgtForm(data=request.POST, instance=user)
        if form.is_valid:
            form.save()
    return render(request, "users/manage.html", context={"form": form, "user": user})


@login_required()
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


@login_required()
def invite_user(request):
    form = InviteUserForm()
    return render(request, "users/invite_user.html", {"form": form})
