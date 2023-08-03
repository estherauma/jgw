from django import forms

from preference.models import Country, FactoryFarm, Organisation


class GenericFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['origin'].queryset = Country.objects.filter(is_origin=True)
        self.fields['destination'].queryset = Country.objects.filter(is_destination=True)
        
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
    
    organisation = forms.ModelMultipleChoiceField(
        queryset=Organisation.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select selectpicker", "data-live-search": "true", "id": "organisation"}),
        required=False
    )
    
    factory_farm = forms.ModelMultipleChoiceField(
        queryset=FactoryFarm.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select selectpicker", "data-live-search": "true", "id": "factory_farm"}),
        required=False
    )