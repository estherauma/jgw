from django import forms
from django.db import models
from pytz import country_names

from .models import Factory, Scheme

DEST_COUNTRIES = {"": "Select a Country"}
ORIGIN_COUNTRIES = {"": "Select a Country"}
FACTORIES = {"": "Select a factory or farm"}

DEST_COUNTRIES.update({k: country_names[k] for k in ("MY", "QA", "SA", "AE", "GB")})
CATEGORIES = ["preferences"]  # , "inline", "messaging", "help_contacts"]


class DependentChoiceField(forms.ChoiceField):
    def valid_value(self, value) -> bool:
        """Check to see if the provided value is a valid choice."""
        text_value = str(value)
        for k, v in country_names.items():
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == str(k2):
                        return True
            else:
                if value == k or text_value == str(k):
                    return True
        return False


class FilterForm(forms.Form):
    destination = forms.ChoiceField(
        choices=DEST_COUNTRIES.items(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-2", "id": "destination"}),
    )
    origin = DependentChoiceField(
        choices=ORIGIN_COUNTRIES.items(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-2", "id": "origin"}),
    )
    scheme_name = forms.ModelChoiceField(
        label="Scheme",
        required=False,
        queryset=Scheme.objects.all(),
        widget=forms.Select(attrs={"class": "form-select mx-2", "id": "scheme_name"}),
    )
    factory_farm = forms.ModelChoiceField(
        label="Factory/Farm",
        queryset=Factory.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-2", "id": "factory_farm"}),
    )


class ExportReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    CATEGORY = models.TextChoices("Category", " ".join(CATEGORIES))
    category = forms.ChoiceField(choices=CATEGORY.choices)
    start_date = forms.DateField()
    end_date = forms.DateField()
