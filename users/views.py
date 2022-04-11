from pydoc import resolve

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CreateUserForm, LoginForm
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
                return redirect("dashboard:index")
            else:
                messages.error(request, "Can not log in with provided credentials!")
        messages.error(request, "Error validating form!")
    return render(request, "users/login.html", {"form": form})
