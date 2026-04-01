from django import forms
from django.forms import ModelForm
from django.db.models import F
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from common.helpers.model_helpers.preference import get_unique_langaues_list

from preference.models import Country, ImmigrationStatus, Organisation, FactoryFarm, OrganisationData

from .models import User, UserInvitations

from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    email = forms.EmailField(
        label=_("LoginFormEmail"),
        error_messages={
            "required": _("loginFormEmailRequired"),
            "invalid": _("loginFormEmailInvalid"),
        })
    password = forms.CharField(
        label=_("LoginFormPassword"),
        error_messages={
            "required": _("loginFormPasswordRequired")
        })

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["password"].widget = forms.PasswordInput(attrs={"autocomplete": "new-password"})
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)
        labels = {
            'email': _('createUserFormEmail'),
        }

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
        fields = ("email", "role", "scheme", "factory", "organisation", "phone_number")

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
        self.fields["email"].label = "Email Address"
        self.fields["phone_number"].label = "Phone Number (optional)"

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists!")
        return cleaned_data


class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField(required=True,
        label=_("requestPasswordResetFormEmail"),
        error_messages={
            "required": _("requestPasswordResetFormEmailRequired"),
            "invalid": _("requestPasswordResetFormEmailInvalid"),
        })
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change their password without entering the old
    password
    """

    error_messages = {
        "password_mismatch": _("setPasswordFormErrorMessage"),
    }
    new_password = forms.CharField(
        label=_("setPasswordFormNewPassword"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    confirm_password = forms.CharField(
        label=_("setPasswordFormConfirmNewPassword"),
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
            "role",
            "scheme",
            "start_date",
            "end_date",
            "factories",
            "organisation_data",
            "organisations",
            "destinations",
            "user_languages",
            "excluded_origin_countries",
            "immigration_status",
            "is_staff",
            "is_superuser",
            "is_active",
            "groups",
            "receive_marketing_emails",
            "dashboard_preferences",
            "dashboard_preferences_version",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["destinations"].queryset = Country.objects.filter(is_destination=True)


class CreateNewUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.fields["destinations"].choices = [
            (country.id, country.name.capitalize())
            for country in Country.objects.filter(is_destination=True).order_by("name")
        ]
        self.fields["excluded_origin_countries"].choices = [
            (country.id, country.name.capitalize())
            for country in Country.objects.filter(is_origin=True).order_by("name")
        ]
        self.fields["factories"].choices = [
            (farm.id, farm.name) for farm in FactoryFarm.objects.all().order_by("name")
        ]
        self.fields["organisation_data"].choices = [
            (org.id, org.name) for org in OrganisationData.objects.all().order_by("name")
        ]
        self.fields["organisations"].choices = [
            (org.id, org.name) for org in Organisation.objects.all().order_by("name")
        ]
        self.fields["user_languages"].choices = [
            (language.id, language.translated_name.capitalize()) for language in get_unique_langaues_list()
        ]

        # groups
        self.fields["groups"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["groups"].widget.attrs["id"] = "user-groups-id"
        self.fields["groups"].widget.attrs["data-live-search"] = "true"

        self.fields["start_date"].widget = forms.DateInput(attrs={"class": "form-control", "type": "date"})
        self.fields["end_date"].widget = forms.DateInput(attrs={"class": "form-control", "type": "date"})

        self.fields["immigration_status"].choices = [
            (status.id, status.name.capitalize())
            for status in ImmigrationStatus.objects.all().order_by("name")
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

    organisation_data = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "create-new-user-organisation-data-id",
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

    immigration_status = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "create-new-user-immigration-status-id",
            }
        ),
        required=False,
    )
    excluded_origin_countries = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "create-new-user-excluded-origin-countries-id",
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
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "password2",
            "start_date",
            "end_date",
            "organisation_data",
            "organisations",
            "factories",
            "destinations",
            "user_languages",
            "excluded_origin_countries",
            "immigration_status",
            "groups",
        ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2


class EditUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(EditUserForm, self).__init__(*args, **kwargs)

        # destination
        self.fields["destinations"].choices = [
            (country.id, country.name.capitalize())
            for country in Country.objects.filter(is_destination=True).order_by("name")
        ]
        self.fields["destinations"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["destinations"].widget.attrs["id"] = "edit-user-destinations-id"
        self.fields["destinations"].widget.attrs["data-live-search"] = "true"

        # language
        self.fields["user_languages"].choices = [
            (language.id, language.translated_name.capitalize()) for language in get_unique_langaues_list()
        ]
        self.fields["user_languages"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["user_languages"].widget.attrs["id"] = "edit-user-languages-id"
        self.fields["user_languages"].widget.attrs["data-live-search"] = "true"

        # organisations
        self.fields["organisations"].choices = [
            (org.id, org.name) for org in Organisation.objects.all().order_by("name")
        ]
        self.fields["organisations"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["organisations"].widget.attrs["id"] = "edit-user-organisations-id"
        self.fields["organisations"].widget.attrs["data-live-search"] = "true"

        # organisation_data
        self.fields["organisation_data"].choices = [
            (org.id, org.name) for org in OrganisationData.objects.all().order_by("name")
        ]
        self.fields["organisation_data"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["organisation_data"].widget.attrs["id"] = "edit-user-organisation-data-id"
        self.fields["organisation_data"].widget.attrs["data-live-search"] = "true"

        # factories
        self.fields["factories"].choices = [
            (farm.id, farm.name) for farm in FactoryFarm.objects.all().order_by("name")
        ]
        self.fields["factories"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["factories"].widget.attrs["id"] = "edit-user-factories-id"
        self.fields["factories"].widget.attrs["data-live-search"] = "true"

        # excluded_origin_countries
        self.fields["excluded_origin_countries"].choices = [
            (country.id, country.name.capitalize())
            for country in Country.objects.filter(is_origin=True).order_by("name")
        ]
        self.fields["excluded_origin_countries"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["excluded_origin_countries"].widget.attrs["id"] = "edit-user-exluded-origin-countries-id"
        self.fields["excluded_origin_countries"].widget.attrs["data-live-search"] = "true"

        self.fields["immigration_status"].choices = [
            (status.id, status.name.capitalize())
            for status in ImmigrationStatus.objects.all().order_by("name")
        ]
        self.fields["immigration_status"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["immigration_status"].widget.attrs["id"] = "edit-user-immigration-status-id"
        self.fields["immigration_status"].widget.attrs["data-live-search"] = "true"

        # groups
        self.fields["groups"].widget.attrs["class"] = "form-select selectpicker"
        self.fields["groups"].widget.attrs["id"] = "user-groups-id"
        self.fields["groups"].widget.attrs["data-live-search"] = "true"

        self.fields["start_date"].widget = forms.DateInput(attrs={"class": "form-control", "type": "date"})
        self.fields["end_date"].widget = forms.DateInput(attrs={"class": "form-control", "type": "date"})

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "start_date",
            "end_date",
            "destinations",
            "user_languages",
            "organisation_data",
            "organisations",
            "factories",
            "destinations",
            "excluded_origin_countries",
            "immigration_status",
            "groups",
        ]
