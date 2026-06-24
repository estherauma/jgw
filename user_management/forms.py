import json
from django import forms
from django.contrib.auth.models import Group
import re
from django.utils import timezone
from django.core.exceptions import ValidationError
from content.models import Collection, Locale, WorkSector
from preference.models import (
    OrganizationGroup,
    OrganisationAccessCode,
    OrganisationData,
    OrganisationDeepLink,
    Country,
    ImmigrationStatus,
    FactoryFarm,
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
from .utils import (
    clean_user_email,
    get_country_code_choices,
    is_org_admin_or_staff,
    validate_password_confirmation,
    validate_user_phone_number,
)


class CreateOrganisationForm(forms.ModelForm):
    ACCESS_CODE_PATTERN = re.compile(r"^\s*[A-Za-z0-9]+(\s*,\s*[A-Za-z0-9]+)*\s*$")
    GENERIC_CUSTOM_CONTENT_COLLECTION_NAME = "Custom-Content-Generic"

    access_code = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control um-input", "placeholder": "Access code"}
        ),
    )
    big_icon_file = forms.FileField(required=False)
    small_icon_file = forms.FileField(required=False)
    content_collection = forms.ModelChoiceField(
        queryset=Collection.objects.none(),
        required=True,
        to_field_name="api_name",
        empty_label="Select content collection",
        widget=forms.Select(attrs={"class": "form-select um-input"}),
    )
    work_sector = forms.ModelChoiceField(
        queryset=WorkSector.objects.none(),
        required=False,
        to_field_name="slug",
        empty_label="Select work sector",
        widget=forms.Select(attrs={"class": "form-select um-input"}),
    )
    collection_languages = forms.ModelMultipleChoiceField(
        queryset=Locale.objects.none(),
        required=True,
        to_field_name="code",
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select um-input",
                "data-role": "collection-language-multiselect",
            }
        ),
    )
    default_collection_language = forms.ModelChoiceField(
        queryset=Locale.objects.none(),
        required=True,
        to_field_name="code",
        empty_label="Select default language",
        widget=forms.Select(attrs={"class": "form-select um-input"}),
    )

    class Meta:
        model = OrganisationData
        fields = [
            "name",
            "org_code",
            "display_name",
            "has_custom_content",
            "content_collection",
            "default_collection_language",
            "work_sector",
            "custom_type",
            "theme",
            "default_report_issue_emails",
            "default_feedback_emails",
            "big_icon",
            "small_icon",
        ]

    @classmethod
    def get_generic_custom_content_collection(cls):
        return Collection.objects.filter(
            name__iexact=cls.GENERIC_CUSTOM_CONTENT_COLLECTION_NAME
        ).first() or Collection.objects.filter(
            api_name__iexact=cls.GENERIC_CUSTOM_CONTENT_COLLECTION_NAME
        ).first()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            "name",
            "org_code",
            "display_name",
            "access_code",
            "content_collection",
            "collection_languages",
            "default_collection_language",
        ]
        optional_fields = [
            "work_sector",
            "theme",
            "default_report_issue_emails",
            "default_feedback_emails",
            "big_icon",
            "small_icon",
            "big_icon_file",
            "small_icon_file",
        ]

        for field_name in required_fields:
            self.fields[field_name].required = True

        for field_name in optional_fields:
            self.fields[field_name].required = False

        self.fields["name"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Organisation name"}
        )
        self.fields["org_code"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Organisation code"}
        )
        self.fields["display_name"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Display name"}
        )
        self.fields["has_custom_content"].widget.attrs.update(
            {"class": "form-check-input", "role": "switch"}
        )
        self.fields["custom_type"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Custom type"}
        )
        self.fields["custom_type"].disabled = True
        self.fields["theme"].widget.attrs.update({"class": "form-select um-input"})
        self.fields["default_report_issue_emails"].widget.attrs.update(
            {
                "class": "form-control um-input",
                "rows": 2,
                "placeholder": "ops@example.com,support@example.com",
            }
        )
        self.fields["default_feedback_emails"].widget.attrs.update(
            {
                "class": "form-control um-input",
                "rows": 2,
                "placeholder": "feedback@example.com",
            }
        )
        self.fields["big_icon"].widget = forms.TextInput(
            attrs={"class": "form-control um-input", "placeholder": "Big icon URL"}
        )
        self.fields["small_icon"].widget = forms.TextInput(
            attrs={"class": "form-control um-input", "placeholder": "Small icon URL"}
        )
        self.fields["big_icon_file"].required = not bool(
            self.instance and self.instance.big_icon
        )
        self.fields["small_icon_file"].required = not bool(
            self.instance and self.instance.small_icon
        )
        collection_qs = Collection.objects.order_by("name")
        work_sector_qs = WorkSector.objects.order_by("display_name")
        language_qs = Locale.objects.order_by("name")
        self.fields["content_collection"].queryset = collection_qs
        self.fields["work_sector"].queryset = work_sector_qs
        self.fields["collection_languages"].queryset = language_qs
        self.fields["default_collection_language"].queryset = language_qs
        self.fields["collection_languages"].widget.attrs.update(
            {"class": "form-select um-input", "size": "5"}
        )
        generic_collection = self.get_generic_custom_content_collection()
        if generic_collection:
            self.fields["content_collection"].widget.attrs.update(
                {
                    "data-generic-collection-value": generic_collection.api_name,
                    "data-generic-collection-label": generic_collection.name,
                    "data-all-options": json.dumps(
                        [{"value": "", "text": "Select content collection"}]
                        + [
                            {"value": collection.api_name, "text": collection.name}
                            for collection in collection_qs
                        ]
                    ),
                }
            )

        if self.instance and self.instance.pk:
            access_code = (
                self.instance.organisation_access_codes.order_by("created_at", "id")
                .values_list("code", flat=True)
                .first()
            )
            if access_code:
                self.fields["access_code"].initial = access_code
            if self.instance.content_collection:
                self.fields["content_collection"].initial = (
                    self.instance.content_collection
                )
            if self.instance.work_sector:
                self.fields["work_sector"].initial = self.instance.work_sector
            self.fields["collection_languages"].initial = list(
                self.instance.collection_languages.values_list("code", flat=True)
            )
            if self.instance.default_collection_language:
                self.fields["default_collection_language"].initial = self.instance.default_collection_language

        has_custom_content_value = None
        if self.is_bound:
            posted_value = self.data.get("has_custom_content")
            has_custom_content_value = posted_value in (True, "true", "True", "on", "1", 1)
        elif self.instance and self.instance.pk:
            has_custom_content_value = self.instance.has_custom_content
        else:
            has_custom_content_value = self.initial.get("has_custom_content", self.fields["has_custom_content"].initial)

        if has_custom_content_value is False and generic_collection:
            self.fields["content_collection"].queryset = Collection.objects.filter(
                pk=generic_collection.pk
            )
            self.fields["content_collection"].initial = generic_collection

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

    def clean_access_code(self):
        access_code = self.cleaned_data.get("access_code", "").strip().upper()
        if access_code and not self.ACCESS_CODE_PATTERN.fullmatch(access_code):
            raise forms.ValidationError(
                "Access code must contain only letters and numbers, optionally separated by commas."
            )
        qs = OrganisationAccessCode.objects.filter(code__iexact=access_code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(organisation=self.instance)
        if qs.exists():
            raise forms.ValidationError("Access code already exists.")
        return access_code

    def clean_default_collection_language(self):
        language = self.cleaned_data.get("default_collection_language")
        return language.code if language else None

    def clean_content_collection(self):
        collection = self.cleaned_data.get("content_collection")
        return collection.api_name if collection else ""

    def clean_work_sector(self):
        work_sector = self.cleaned_data.get("work_sector")
        return work_sector.slug if work_sector else ""

    def clean(self):
        cleaned_data = super().clean()
        strip_fields = [
            "display_name",
            "access_code",
            "content_collection",
            "work_sector",
            "custom_type",
            "theme",
            "default_report_issue_emails",
            "default_feedback_emails",
            "big_icon",
            "small_icon",
        ]
        for field_name in strip_fields:
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()

        has_custom_content = cleaned_data.get("has_custom_content")
        generic_collection = self.get_generic_custom_content_collection()
        if has_custom_content is False:
            if not generic_collection:
                self.add_error(
                    "content_collection",
                    "Custom content generic collection was not found.",
                )
            else:
                cleaned_data["content_collection"] = generic_collection.api_name

        collection_languages = cleaned_data.get("collection_languages") or []
        default_collection_language = cleaned_data.get("default_collection_language")
        selected_language_codes = {language.code for language in collection_languages}

        if (
            default_collection_language
            and default_collection_language not in selected_language_codes
        ):
            self.add_error(
                "default_collection_language",
                "Default collection language must be one of the selected collection languages.",
            )

        return cleaned_data

class CreateOrganizationGroupForm(forms.ModelForm):
    class Meta:
        model = OrganizationGroup
        fields = ["name", "group_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Organization group name"}
        )
        self.fields["group_code"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Group code"}
        )

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip().title()
        qs = OrganizationGroup.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Organization group name already exists.")
        return name

    def clean_group_code(self):
        group_code = self.cleaned_data.get("group_code", "").strip().upper()
        qs = OrganizationGroup.objects.filter(group_code__iexact=group_code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Group code already exists.")
        return group_code


class EditOrganizationGroupForm(forms.ModelForm):
    class Meta:
        model = OrganizationGroup
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Brand name"}
        )

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip().title()
        qs = OrganizationGroup.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Organization group name already exists.")
        return name


class AttachOrganizationsToGroupForm(forms.Form):
    organizations = forms.ModelMultipleChoiceField(
        queryset=OrganisationData.objects.none(),
        required=True,
        widget=forms.SelectMultiple(attrs={"class": "form-select um-input"}),
    )

    def __init__(self, *args, **kwargs):
        organisations_qs = kwargs.pop("organisations_qs", OrganisationData.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["organizations"].queryset = organisations_qs.order_by("name")


class AddWorkCodeForm(forms.ModelForm):
    WORK_CODE_PATTERN = re.compile(r"^[A-Za-z0-9]+$")

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
        if code and not self.WORK_CODE_PATTERN.fullmatch(code):
            raise forms.ValidationError(
                "Work code must contain only letters and numbers."
            )
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
        required=True,
        widget=forms.SelectMultiple(),
    )
    organisation_group = forms.ModelChoiceField(
        queryset=OrganizationGroup.objects.none(),
        required=False,
        empty_label="",
        widget=forms.Select(),
    )
    organisation_data = forms.ModelMultipleChoiceField(
        queryset=OrganisationData.objects.none(),
        required=False,
        widget=forms.SelectMultiple(),
    )
    factories = forms.ModelMultipleChoiceField(
        queryset=FactoryFarm.objects.none(),
        required=False,
        widget=forms.SelectMultiple(),
    )
    destinations = forms.ModelMultipleChoiceField(
        queryset=Country.objects.none(),
        required=False,
        widget=forms.SelectMultiple(),
    )
    user_languages = forms.ModelMultipleChoiceField(
        queryset=Locale.objects.none(),
        required=False,
        widget=forms.SelectMultiple(),
    )
    excluded_origin_countries = forms.ModelMultipleChoiceField(
        queryset=Country.objects.none(),
        required=False,
        widget=forms.SelectMultiple(),
    )
    immigration_status = forms.ModelMultipleChoiceField(
        queryset=ImmigrationStatus.objects.none(),
        required=False,
        widget=forms.SelectMultiple(),
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
            "organisation_group",
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
        for field_name in [
            "groups",
            "organisation_group",
            "organisation_data",
            "factories",
            "destinations",
            "user_languages",
            "excluded_origin_countries",
            "immigration_status",
        ]:
            self.fields[field_name].widget.attrs.update({"class": "form-control um-input"})
        if orgs_qs is not None:
            self.fields["organisation_data"].queryset = orgs_qs
            self.fields["organisation_group"].queryset = (
                OrganizationGroup.objects.filter(organizations__in=orgs_qs)
                .distinct()
                .order_by("name")
            )
        else:
            self.fields["organisation_group"].queryset = OrganizationGroup.objects.order_by(
                "name"
            )
        self.fields["scheme"].queryset = Scheme.objects.all().order_by("name")
        self.fields["factories"].queryset = FactoryFarm.objects.all().order_by("name")
        self.fields["destinations"].queryset = Country.objects.filter(
            is_destination=True
        ).order_by("name")
        self.fields["user_languages"].queryset = Locale.objects.all().order_by("name")
        self.fields["excluded_origin_countries"].queryset = Country.objects.filter(
            is_origin=True
        ).order_by("name")
        self.fields["immigration_status"].queryset = ImmigrationStatus.objects.all().order_by("name")
        if self.instance and self.instance.pk:
            self.initial["organisation_group"] = self.instance.organization_group_id

    def clean_email(self):
        return clean_user_email(
            self.cleaned_data.get("email"),
            instance=self.instance,
            required=True,
        )

    def clean(self):
        cleaned = super().clean()
        admin_groups = cleaned.get("groups")
        organisation_group = cleaned.get("organisation_group")
        organisation_data = cleaned.get("organisation_data")
        selected_group_names = {group.name for group in admin_groups} if admin_groups else set()
        is_org_group_admin = "org_group_admin" in selected_group_names
        is_58_admin_selected = "58_admin" in selected_group_names

        validate_password_confirmation(self, cleaned, "password", "password_confirm")

        if is_58_admin_selected:
            cleaned["organisation_group"] = None
            cleaned["organisation_data"] = OrganisationData.objects.none()
            cleaned["scheme"] = None
            cleaned["start_date"] = None
            cleaned["end_date"] = None
            cleaned["factories"] = FactoryFarm.objects.none()
            cleaned["destinations"] = Country.objects.none()
            cleaned["user_languages"] = Locale.objects.none()
            cleaned["excluded_origin_countries"] = Country.objects.none()
            cleaned["immigration_status"] = ImmigrationStatus.objects.none()
        elif is_org_group_admin:
            if not organisation_group:
                self.add_error(
                    "organisation_group",
                    "Select an organisation group for org group admins.",
                )
            cleaned["organisation_data"] = OrganisationData.objects.none()
            cleaned["scheme"] = None
            cleaned["start_date"] = None
            cleaned["end_date"] = None
            cleaned["factories"] = FactoryFarm.objects.none()
            cleaned["destinations"] = Country.objects.none()
            cleaned["user_languages"] = Locale.objects.none()
            cleaned["excluded_origin_countries"] = Country.objects.none()
            cleaned["immigration_status"] = ImmigrationStatus.objects.none()
        elif admin_groups and not organisation_data:
            cleaned["organisation_group"] = None
            has_org_scoped_role = any(
                group.name in {"org_admin", "org_staff"}
                for group in admin_groups
            )
            if has_org_scoped_role:
                self.add_error(
                    "organisation_data",
                    "Select an organisation",
                )
        else:
            cleaned["organisation_group"] = None

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        admin_groups = self.cleaned_data.get("groups")
        selected_group_names = {group.name for group in admin_groups} if admin_groups else set()
        if "org_group_admin" in selected_group_names:
            user.organization_group = self.cleaned_data.get("organisation_group")
        else:
            user.organization_group = None
        if commit:
            user.save()
            self.save_m2m()
        return user


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
        self.fields["work_groups"].widget = forms.SelectMultiple(
            attrs={"class": "form-control um-input"}
        )

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
        return clean_user_email(self.cleaned_data.get("email"), instance=self.instance)

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        phone_number = cleaned.get("phone_number", "") or ""
        email = (cleaned.get("email") or "").strip()
        validate_password_confirmation(self, cleaned, "password", "password_confirm")
        if role and not role.grants_dashboard_access and not email and not phone_number:
            self.add_error(
                "email",
                "Provide an email or phone number for app users.",
            )
        if role and role.grants_dashboard_access and not email:
            self.add_error("email", "Email is required for dashboard users.")
        validate_user_phone_number(self, cleaned)
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


class OrganisationDeepLinkForm(forms.ModelForm):
    destination = forms.ModelChoiceField(
        queryset=Country.objects.none(),
        required=True,
        empty_label="Select destination",
        widget=forms.Select(attrs={"class": "form-select um-input"}),
    )
    access_code = forms.ModelChoiceField(
        queryset=OrganisationAccessCode.objects.none(),
        required=False,
        empty_label="Select access code",
        widget=forms.Select(attrs={"class": "form-select um-input"}),
    )
    sectors = forms.ModelChoiceField(
        queryset=WorkSector.objects.none(),
        required=False,
        empty_label="Select sector",
        widget=forms.Select(attrs={"class": "form-select um-input"}),
        to_field_name="slug",
    )
    immigration_status = forms.ModelChoiceField(
        queryset=ImmigrationStatus.objects.none(),
        required=False,
        empty_label="Select immigration status",
        widget=forms.Select(attrs={"class": "form-select um-input"}),
    )

    class Meta:
        model = OrganisationDeepLink
        fields = ["title", "link_type"]

    def __init__(self, *args, **kwargs):
        self.organisation = kwargs.pop("organisation", None)
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["link_type"].required = True
        self.fields["destination"].required = True
        self.fields["access_code"].required = False
        self.fields["sectors"].required = False
        self.fields["immigration_status"].required = False
        self.fields["title"].widget.attrs.update(
            {"class": "form-control um-input", "placeholder": "Link title"}
        )
        self.fields["link_type"].widget.attrs.update(
            {
                "class": "form-control um-input",
                "placeholder": "Link type",
                "readonly": "readonly",
            }
        )
        self.fields["link_type"].initial = (
            self.initial.get("link_type")
            or getattr(self.instance, "link_type", None)
            or "onboarding"
        )
        self.fields["link_type"].disabled = True
        self.fields["destination"].queryset = Country.objects.filter(
            is_destination=True
        ).order_by("name")
        self.fields["access_code"].queryset = (
            OrganisationAccessCode.objects.filter(organisation=self.organisation)
            .prefetch_related("work_groups")
            .order_by("code")
            if self.organisation
            else OrganisationAccessCode.objects.none()
        )
        self.fields["sectors"].queryset = WorkSector.objects.order_by(
            "display_name"
        )
        self.fields["immigration_status"].queryset = ImmigrationStatus.objects.order_by(
            "name"
        )
        self.fields["access_code"].label_from_instance = self.get_access_code_label
        self.fields["sectors"].label_from_instance = lambda sector: sector.display_name
        self.fields["destination"].label_from_instance = (
            self.get_destination_label
        )
        self.fields["immigration_status"].label_from_instance = (
            lambda status: status.name
        )

    @staticmethod
    def get_access_code_label(access_code):
        group_names = sorted(group.name for group in access_code.work_groups.all())
        group_label = ", ".join(group_names) if group_names else "All users"
        return f"{access_code.code} ({group_label})"

    @staticmethod
    def get_destination_label(destination):
        name = destination.name or ""
        if not name:
            return ""
        return name[:1].upper() + name[1:]

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        return title

    def clean_link_type(self):
        link_type = (
            (self.cleaned_data.get("link_type") or "")
            or self.fields["link_type"].initial
            or "onboarding"
        )
        link_type = str(link_type).strip().lower()
        if not link_type:
            raise forms.ValidationError("Link type is required.")
        return link_type

    def save(self, commit=True, generated_link=None):
        deep_link = super().save(commit=False)
        if self.organisation:
            deep_link.organisation = self.organisation
        if generated_link is not None:
            deep_link.link = generated_link
        if commit:
            if not deep_link.link:
                raise ValidationError("Generated link is required.")
            deep_link.save()
        return deep_link


class WorkCodeAssignForm(forms.Form):
    work_groups = forms.ModelMultipleChoiceField(
        queryset=WorkGroup.objects.none(),
        required=False,
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
