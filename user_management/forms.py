from django import forms

from preference.models import OrganisationData


class CreateOrganisationForm(forms.ModelForm):
    class Meta:
        model = OrganisationData
        fields = ["name", "org_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control form-control-sm um-input", "placeholder": "Organisation name"}
        )
        self.fields["org_code"].widget.attrs.update(
            {"class": "form-control form-control-sm um-input", "placeholder": "Organisation code"}
        )

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip().title()
        if OrganisationData.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Organisation name already exists.")
        return name

    def clean_org_code(self):
        org_code = self.cleaned_data.get("org_code", "").strip().upper()
        if OrganisationData.objects.filter(org_code__iexact=org_code).exists():
            raise forms.ValidationError("Organisation code already exists.")
        return org_code
