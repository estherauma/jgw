from django import forms
from pytz import country_names

DEST_COUNTRIES = {"": "Select a country"}
ORIGIN_COUNTRIES = {"": "Select a Country"}
DEST_COUNTRIES.update({k: country_names[k] for k in ("MY", "QA", "SA", "AE", "GB")})


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
    scheme_name = forms.CharField(required=False)
    # factory_farm = DependentChoiceField(
    #     required=False,
    #     widget=forms.Select(attrs={"class": "form-select mx-2", "id": "origin"}),
    # )
