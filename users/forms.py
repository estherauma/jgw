from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm

from .models import User


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["password"].widget = forms.PasswordInput(attrs={"autocomplete": "new-password"})
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
