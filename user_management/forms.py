from django import forms
from django.core.exceptions import ValidationError

import phonenumbers
from django.utils import timezone
from django.core.exceptions import ValidationError
from preference.models import OrganisationAccessCode, OrganisationData
from .models import AppUser, WorkGroup
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


class AppUserForm(forms.ModelForm):
    phone_country_iso = forms.ChoiceField(required=False)

    class Meta:
        model = AppUser
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
        self.fields["email"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Email"}
        )
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "First name"}
        )
        self.fields["last_name"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Last name"}
        )
        self.fields["phone_number"].widget.attrs.update(
            {"class": "form-control  um-input", "placeholder": "Phone number (optional)"}
        )
        self.fields["phone_country_iso"].choices = get_country_code_choices()
        self.fields["phone_country_iso"].widget.attrs.update(
            {"class": "form-control  um-input"}
        )
        self.fields["work_groups"].widget = forms.CheckboxSelectMultiple()
        if work_groups_qs is not None:
            self.fields["work_groups"].queryset = work_groups_qs

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        qs = AppUser.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        phone_number = cleaned.get("phone_number", "") or ""
        phone_country_iso = cleaned.get("phone_country_iso", "") or ""
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
            phone_qs = AppUser.objects.filter(
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
