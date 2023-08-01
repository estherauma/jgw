from django import forms

from preference.models import Country


class GenericFilterForm(forms.Form):
    start_date = forms.DateField(
        label='Start Date',
        required=False,
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={"type": "date"},
        ),
    )
    end_date = forms.DateField(
        label='End Date', 
        required=False,
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={"type": "date"},
        )
    )

    destination = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select selectpicker", "data-live-search": "true", "id": "destination"}),
        required=False
    )

    origin = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select selectpicker", "data-live-search": "true", "id": "origin"}),
        required=False
    )