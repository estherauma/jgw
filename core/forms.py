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

    destination = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False
    )

    origin = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False
    )