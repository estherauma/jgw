from pydoc import resolve

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, resolve_url

from .forms import CreateUserForm, LoginForm
from .models import User


@login_required()
def list_users(request):
    queryset = User.objects.all()
    return render(request, "users/list.html", context={"users": queryset})


def create_user_account(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            messages.info(request, "Account created. Contact admin to activate.")
            return redirect("users:login_user")
        return render(request, "users/create.html", {"form": form})
    return render(request, "users/create.html", context={"form": form})


def login_user(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = User.objects.filter(email=email).first()
            if user is None:
                messages.error(request, "Account with given credentials not found!")
            if not user.is_active:
                messages.info(request, "This account is not active, contact admin to activate.")
            user = authenticate(username=email, password=password)
            if user is None:
                messages.error(request, "Invalid credentials")
            login(request, user)
            return resolve_url("dashboard:index")
        else:
            messages.error(request, "Error validating the form")
        return render(request, "users/login.html", {"form": form})
    return render(request, "users/login.html", {"form": form})
