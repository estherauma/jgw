from django import forms
from django.contrib.auth.forms import UserCreationForm

from dashboard.forms import OPERATORS
from dashboard.models import Factory, Scheme

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
            self.fields[field].widget.attrs["class"] = "form-control mx-2"


class UserMgtForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("is_active", "scheme", "factory", "role")

    def __init__(self, *args, **kwargs):
        super(UserMgtForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control mx-2"
            self.fields[field].required = False


class InviteUserForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control mx-2"

    email = forms.EmailField(label="Email Address", required=True)
    role = forms.ChoiceField(required=True, choices=User.ROLE.choices)
    scheme = forms.ChoiceField(required=False, choices=Scheme.objects.all())
    factory_farm = forms.ChoiceField(label="Factory/Farm", choices=Factory.objects.all(), required=False)
    organisation = forms.ChoiceField(required=False, choices=OPERATORS.items())
