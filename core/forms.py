from django import forms

from preference.models import Country, FactoryFarm, Organisation


class GenericFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['origin'].choices = [
            (country.name, country.name)
            for country in Country.objects.filter(is_origin=True)
        ]
        
        self.fields['destination'].choices = [
            (country.name, country.name)
            for country in Country.objects.filter(is_destination=True)
        ]

        self.fields["factory_farm"].choices = [
            (farm.name, farm.name) for farm in FactoryFarm.objects.all()
        ]
        
        self.fields["organisation"].choices = [
            (org.name, org.name) for org in Organisation.objects.all()
        ]
        
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

    origin = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            "class": "form-select selectpicker", 
            "data-live-search": "true", 
            "id": "origin"
        }),
        required=False
    )
    
    destination = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            "class": "form-select selectpicker", 
            "data-live-search": "true", 
            "id": "destination"
        }),
        required=False
    )
    
    organisation = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            "class": "form-select selectpicker", 
            "data-live-search": "true",
            "id": "organisation"
        }),
        required=False
    )
    
    factory_farm = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            "class": "form-select selectpicker", 
            "data-live-search": "true", 
            "id": "factory_farm"
        }),
        required=False
    )