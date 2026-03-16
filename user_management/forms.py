from django import forms
from django.contrib.auth.models import Group

import phonenumbers
from django.utils import timezone
from django.core.exceptions import ValidationError
from preference.models import (
    OrganisationAccessCode,
    OrganisationData,
    Country,
    ImmigrationStatus,
    FactoryFarm,
    Language,
)
from dashboard.models import Scheme
from users.models import User
from .models import WorkGroup
from .utils import get_country_code_choices, validate_phone_number


class CreateOrganisationForm(forms.ModelForm):
    class Meta:
        model = OrganisationData
        fields = ["name", "org_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Organisation name"}
        )
        self.fields["org_code"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Organisation code"}
        )

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip().title()
        qs = OrganisationData.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Organisation name already exists.")
        return name

    def clean_org_code(self):
        org_code = self.cleaned_data.get("org_code", "").strip().upper()
        qs = OrganisationData.objects.filter(org_code__iexact=org_code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Organisation code already exists.")
        return org_code


class AddWorkCodeForm(forms.ModelForm):
    class Meta:
        model = OrganisationAccessCode
        fields = ["code", "expiry_date", "requires_login"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Work code"}
        )
        self.fields["expiry_date"].widget = forms.DateInput(
            attrs={"type": "date", "class": "form-control um-input"},
        )
        self.fields["requires_login"].widget.attrs.update(
            {"class": "form-check-input", "role": "switch"}
        )
        
    def validate_unique(self):
        exclude = self._get_validation_exclusions()
    
        if 'code' not in exclude:
            exclude.append('code')
        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError as e:
            self._update_errors(e)

    def clean_code(self):
        code = self.cleaned_data.get("code", "").strip().upper()
        return code
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get("expiry_date")
        if expiry_date and expiry_date < timezone.now().date():
            raise forms.ValidationError("Expiry date cannot be in the past.")
        return expiry_date


class WorkGroupForm(forms.ModelForm):
    class Meta:
        model = WorkGroup
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Work group name"}
        )

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        return name


class DashboardUserForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    organisation_data = forms.ModelMultipleChoiceField(
        queryset=OrganisationData.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    factories = forms.ModelMultipleChoiceField(
        queryset=FactoryFarm.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    destinations = forms.ModelMultipleChoiceField(
        queryset=Country.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    user_languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    excluded_origin_countries = forms.ModelMultipleChoiceField(
        queryset=Country.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    immigration_status = forms.ModelMultipleChoiceField(
        queryset=ImmigrationStatus.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False)
    is_active = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "scheme",
            "start_date",
            "end_date",
            "is_active",
            "groups",
            "organisation_data",
            "factories",
            "destinations",
            "user_languages",
            "excluded_origin_countries",
            "immigration_status",
        ]

    def __init__(self, *args, **kwargs):
        orgs_qs = kwargs.pop("orgs_qs", None)
        super().__init__(*args, **kwargs)
        groups_qs = Group.objects.exclude(name="worker").order_by("name")
        self.fields["groups"].queryset = groups_qs
        self.fields["email"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Email"}
        )
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "First name"}
        )
        self.fields["last_name"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Last name"}
        )
        self.fields["scheme"].widget.attrs.update({"class": "form-control um-input"})
        self.fields["start_date"].widget = forms.DateInput(
            attrs={"class": "form-control um-input", "type": "date"}
        )
        self.fields["end_date"].widget = forms.DateInput(
            attrs={"class": "form-control um-input", "type": "date"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Password"}
        )
        self.fields["password_confirm"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Confirm password"}
        )
        self.fields["is_active"].widget = forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        )
        if orgs_qs is not None:
            self.fields["organisation_data"].queryset = orgs_qs
        self.fields["scheme"].queryset = Scheme.objects.all().order_by("name")
        self.fields["factories"].queryset = FactoryFarm.objects.all().order_by("name")
        self.fields["destinations"].queryset = Country.objects.filter(
            is_destination=True
        ).order_by("name")
        self.fields["user_languages"].queryset = Language.objects.all().order_by("translated_name")
        self.fields["excluded_origin_countries"].queryset = Country.objects.filter(
            is_origin=True
        ).order_by("name")
        self.fields["immigration_status"].queryset = ImmigrationStatus.objects.all().order_by("name")

    def clean_email(self):
        email = self.cleaned_data.get("email") or ""
        email = email.strip().lower()
        if not email:
            raise forms.ValidationError("Email is required")
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        password_confirm = cleaned.get("password_confirm")
        admin_groups = cleaned.get("groups")
        organisation_data = cleaned.get("organisation_data")

        if password or password_confirm:
            if password != password_confirm:
                self.add_error("password_confirm", "Passwords do not match.")

        if admin_groups and not organisation_data:
            has_org_admin = any(group.name == "org_admin" for group in admin_groups)
            if has_org_admin:
                self.add_error(
                    "organisation_data",
                    "Select at least one organisation for org admins.",
                )

        return cleaned


class AppUserForm(forms.ModelForm):
    role_group = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        required=True,
    )
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False)
    phone_country_iso = forms.ChoiceField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "phone_country_iso",
            "work_groups",
        ]

    def __init__(self, *args, **kwargs):
        work_groups_qs = kwargs.pop("work_groups_qs", None)
        super().__init__(*args, **kwargs)
        role_names = ["org_admin", "worker"]
        for role_name in role_names:
            Group.objects.get_or_create(name=role_name)
        self.fields["role_group"].label_from_instance = (
            lambda group: "Administrator" if group.name == "org_admin" else "Worker"
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Email"}
        )
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "First name"}
        )
        self.fields["last_name"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Last name"}
        )
        self.fields["phone_number"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Phone number (optional)"}
        )
        self.fields["phone_country_iso"].choices = get_country_code_choices()
        self.fields["phone_country_iso"].widget.attrs.update(
            {"class": "form-control um-input"}
        )
        self.fields["work_groups"].widget = forms.CheckboxSelectMultiple()

        self.fields["password"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Password"}
        )
        self.fields["password_confirm"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Confirm password"}
        )
        self.fields["role_group"].widget = forms.Select(
            attrs={
                "class": "form-control um-input",
            }
        )
        self.fields["role_group"].queryset = Group.objects.filter(
            name__in=role_names
        ).order_by("name")

        if work_groups_qs is not None:
            self.fields["work_groups"].queryset = work_groups_qs

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        qs = User.objects.filter(email__iexact=email)

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role_group")
        phone_number = cleaned.get("phone_number", "") or ""
        phone_country_iso = cleaned.get("phone_country_iso", "") or ""
        email = (cleaned.get("email") or "").strip()
        password = cleaned.get("password")
        password_confirm = cleaned.get("password_confirm")
        if password or password_confirm:
            if password != password_confirm:
                self.add_error("password_confirm", "Passwords do not match.")
        if role and role.name == "worker" and not email and not phone_number:
            self.add_error(
                "email",
                "Provide an email or phone number for workers.",
            )
        if role and role.name == "org_admin" and not email:
            self.add_error("email", "Email is required for org admins.")
        if phone_number and not phone_country_iso:
            self.add_error("phone_country_iso", "Select a country code.")
            return cleaned
        if phone_number and phone_country_iso:
            parsed, error_message = validate_phone_number(phone_number, phone_country_iso)
            if error_message:
                if "country code" in error_message:
                    self.add_error("phone_country_iso", error_message)
                else:
                    self.add_error("phone_number", error_message)
                return cleaned
            cleaned["phone_number"] = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
            phone_qs = User.objects.filter(
                phone_number=cleaned["phone_number"],
                phone_country_iso=phone_country_iso,
            )
            if self.instance and self.instance.pk:
                phone_qs = phone_qs.exclude(pk=self.instance.pk)
            if phone_qs.exists():
                self.add_error(
                    "phone_number",
                    "Phone number already exists for the selected country.",
                )
        return cleaned


class WorkCodeAssignForm(forms.Form):
    work_groups = forms.ModelMultipleChoiceField(
        queryset=WorkGroup.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        work_groups_qs = kwargs.pop("work_groups_qs", None)
        super().__init__(*args, **kwargs)
        if work_groups_qs is not None:
            self.fields["work_groups"].queryset = work_groups_qs


class UsersWorkGroupAssignForm(forms.Form):
    work_groups = forms.ModelMultipleChoiceField(
        queryset=WorkGroup.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        work_groups_qs = kwargs.pop("work_groups_qs", None)
        super().__init__(*args, **kwargs)
        if work_groups_qs is not None:
            self.fields["work_groups"].queryset = work_groups_qs
