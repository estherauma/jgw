from django import forms
from django.forms import ModelForm
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from common.helpers.model_helpers.preference import get_unique_langaues_list

from preference.models import Country, Organisation, FactoryFarm

from .models import User, UserInvitations


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


class UserMgtForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("is_active", "scheme", "role")

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields[field].required = False
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"


class InviteUserForm(forms.ModelForm):
    class Meta:
        model = UserInvitations
        fields = ("email", "role", "scheme")

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
        self.fields["email"].label = "Email Address"

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists!")
        return cleaned_data


class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    error_messages = {
        "password_mismatch": "The two password fields didn’t match.",
    }
    new_password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    confirm_password = forms.CharField(
        label="Confirm new password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean_confirm_password(self):
        password = self.cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        password_validation.validate_password(confirm_password)
        return confirm_password


class ChangeEmailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    new_email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"placeholder": "New Email Address"})
    )


class UpdateUserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "receive_marketing_emails")

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

            if field == "receive_marketing_emails":
                self.fields[field].widget.attrs["class"] = "form-check-input"


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "scheme",
            "factories",
            "organisations",
            "destinations",
            "user_languages",
            "is_staff",
            "is_superuser",
            "is_active",
            "groups",
            "receive_marketing_emails",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["destinations"].queryset = Country.objects.filter(is_destination=True)


class CreateNewUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["destinations"].choices = [
            (country.id, country.name.capitalize()) for country in Country.objects.all()
        ]
        self.fields["factories"].choices = [(farm.id, farm.name) for farm in FactoryFarm.objects.all()]
        self.fields["organisations"].choices = [(org.id, org.name) for org in Organisation.objects.all()]
        self.fields["user_languages"].choices = [
            (language.id, language.translated_name.capitalize()) for language in get_unique_langaues_list()
        ]

    organisations = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "create-new-user-organisations-id",
            }
        ),
        required=False,
    )
    factories = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "create-new-user-factory-farms-id",
            }
        ),
        required=False,
    )
    destinations = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "create-new-user-destinations-id",
            }
        ),
        required=False,
    )
    user_languages = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "excepted-languages-search-id",
            }
        ),
        required=False,
    )
    password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "organisations",
            "factories",
            "destinations",
            "user_languages",
        ]
