from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from .models import User


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)
