import ast

from django import forms
from pytz import country_names


class FilterForm(forms.Form):
    destination = forms.CharField(
        required=False,
        widget=forms.SelectMultiple(
            choices=country_names.items(), attrs={"class": "form-select", "size": "3"}
        ),
    )

    def clean_destination(self):
        # convert from string enclosed list to list literal
        return ast.literal_eval(self.cleaned_data["destination"])
