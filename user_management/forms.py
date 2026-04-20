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
from waffle.models import Flag

from .models import (
    OrganisationRole,
    OrganisationRolePermission,
    WorkGroup,
)
from .flags import UM_FLAG_DEFS
from .utils import get_country_code_choices, is_org_admin_or_staff, validate_phone_number


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
        if self.instance and self.instance.pk:
            self.fields['code'].disabled = True
        
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
        today = timezone.now().date()
        if expiry_date:
            if expiry_date <= today:
                raise forms.ValidationError("Expiry date must be a future date.")
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
    send_invite = forms.BooleanField(required=False, initial=True)

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
        groups_qs = Group.objects.exclude(name__in=["worker", "org_staff"]).order_by("name")
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
        self.fields["send_invite"].widget = forms.CheckboxInput(
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
        qs = User.all_objects.filter(email__iexact=email)
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
    role = forms.ModelChoiceField(queryset=OrganisationRole.objects.none(), required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False)
    phone_country_iso = forms.ChoiceField(required=False)
    send_invite = forms.BooleanField(required=False, initial=True)

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
        organisation = kwargs.pop("organisation", None)
        super().__init__(*args, **kwargs)

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
        self.fields["role"].widget = forms.Select(
            attrs={
                "class": "form-control um-input",
            }
        )
        self.fields["send_invite"].widget = forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        )
        if organisation:
            self.fields["role"].queryset = OrganisationRole.objects.filter(
                organisation=organisation
            ).order_by("name")

        if work_groups_qs is not None:
            self.fields["work_groups"].queryset = work_groups_qs

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            return None
        qs = User.all_objects.filter(email__iexact=email)

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        phone_number = cleaned.get("phone_number", "") or ""
        phone_country_iso = cleaned.get("phone_country_iso", "") or ""
        email = (cleaned.get("email") or "").strip()
        password = cleaned.get("password")
        password_confirm = cleaned.get("password_confirm")
        if password or password_confirm:
            if password != password_confirm:
                self.add_error("password_confirm", "Passwords do not match.")
        if role and not role.grants_dashboard_access and not email and not phone_number:
            self.add_error(
                "email",
                "Provide an email or phone number for app users.",
            )
        if role and role.grants_dashboard_access and not email:
            self.add_error("email", "Email is required for dashboard users.")
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


class OrganisationRoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Flag.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = OrganisationRole
        fields = ["name", "description", "grants_dashboard_access"]

    def __init__(self, *args, **kwargs):
        self.organisation = kwargs.pop("organisation", None)
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)
        flag_labels = {flag["name"]: flag.get("label", flag["name"]) for flag in UM_FLAG_DEFS}
        self.fields["name"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Role name"}
        )
        self.fields["description"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Role description"}
        )
        self.fields.pop("grants_dashboard_access", None)
        um_flags = UM_FLAG_DEFS
        if self.current_user and is_org_admin_or_staff(self.current_user):
            um_flags = [flag for flag in UM_FLAG_DEFS if flag.get("condition") == "org_admin"]
        um_flag_names = [flag["name"] for flag in um_flags]
        self.fields["permissions"].queryset = Flag.objects.filter(
            name__in=um_flag_names
        ).order_by("name")
        self.fields["permissions"].label_from_instance = lambda flag: flag_labels.get(
            flag.name, flag.name
        )
        if self.instance and self.instance.pk:
            selected = OrganisationRolePermission.objects.filter(
                role=self.instance
            ).values_list("flag_id", flat=True)
            self.fields["permissions"].initial = list(selected)

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Role name is required.")
        if self.organisation:
            qs = OrganisationRole.objects.filter(
                organisation=self.organisation, name__iexact=name
            )
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Role name already exists.")
        return name

    def save(self, commit=True):
        role = super().save(commit=False)
        if self.organisation:
            role.organisation = self.organisation
        role.grants_dashboard_access = role.name != "Worker"
        if commit:
            role.save()
        permissions = self.cleaned_data.get("permissions", [])
        OrganisationRolePermission.objects.filter(role=role).exclude(
            flag__in=permissions
        ).delete()
        existing_flags = set(
            OrganisationRolePermission.objects.filter(role=role).values_list(
                "flag_id", flat=True
            )
        )
        new_permissions = [
            OrganisationRolePermission(role=role, flag=flag)
            for flag in permissions
            if flag.id not in existing_flags
        ]
        if new_permissions:
            OrganisationRolePermission.objects.bulk_create(new_permissions)
        return role


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
