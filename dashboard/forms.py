from django import forms
from pytz import country_names

DEST_COUNTRIES = {"": "Select a country"}
ORIGIN_COUNTRIES = {"": "Select a country"}
DEST_COUNTRIES.update({k: country_names[k] for k in ("MY", "QA", "SA", "AE", "GB")})
ORIGIN_COUNTRIES.update({k: country_names[k] for k in ("UG", "KY", "TZ", "MM", "NP", "VN")})


class FilterForm(forms.Form):
    destination = forms.ChoiceField(
        choices=DEST_COUNTRIES.items(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-2"}),
    )
    origin = forms.ChoiceField(
        choices=ORIGIN_COUNTRIES.items(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-2"}),
    )

    # def clean_destination(self):
    #     # convert from string enclosed list to list literal when using SelectMultiple
    #     import ast
    #     return ast.literal_eval(self.cleaned_data["destination"])
