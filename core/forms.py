from datetime import datetime
from django import forms
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.helpers.model_helpers.preference import get_countries_without_excluded_names

from preference.models import CountryState, ImmigrationStatus
from users.utils import (
    get_user_factories,
    get_user_group,
    get_user_organisations,
    get_user_destinations,
    get_user_start_date,
    get_user_end_date,
    get_user_immigration_status,
)


class GenericFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.fields["origin"].choices = sorted(self.get_countries({"is_origin": True}))
        self.fields["destination"].choices = sorted(self.get_countries({"is_destination": True}))

        user_factories = get_user_factories(self.request.user)
        user_orgs = get_user_organisations(self.request.user)
        user_group = get_user_group(self.request.user)
        user_immigration_status = get_user_immigration_status(self.request.user)

        self.fields["factory_farm"].choices = sorted([(farm.name, farm.name) for farm in user_factories])
        self.fields["organisation"].choices = sorted([(org_info.name, org_info.name) for org_info in user_orgs])

        if user_immigration_status:
            choices = [(status.name, status.name.capitalize()) for status in user_immigration_status]
        else:
            choices = [(status.name, status.name.capitalize()) for status in ImmigrationStatus.objects.all()]

        self.fields["immigration_status"].choices = sorted(choices)
        self.fields["immigration_status"].widget.attrs.update(
            {
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "immigration_status",
                "data-actions-box": "true",
            }
        )

        if "SWSConfig" in user_group:
            self.fields["organisation"].widget.attrs["disabled"] = True

        user_start_date = get_user_start_date(self.request.user) or APPLICATION_POSSIBLE_START_DATE
        user_end_date = get_user_end_date(self.request.user) or datetime.now().date()

        if user_start_date:
            self.fields["start_date"].widget.attrs["min"] = user_start_date
            self.fields["end_date"].widget.attrs["min"] = user_start_date
        if user_end_date:
            self.fields["start_date"].widget.attrs["max"] = user_end_date
            self.fields["end_date"].widget.attrs["max"] = user_end_date

    def get_countries(self, countries_filter):
        countries = []
        countries_to_get_states_from = []

        if countries_filter.get("is_destination"):
            countries_to_get_states_from = get_user_destinations(self.request.user)
        else:
            countries_to_get_states_from = get_countries_without_excluded_names(filter=countries_filter)

        for country in countries_to_get_states_from:
            country_states = CountryState.objects.filter(country=country)
            states_list = [(state.name, state.full_name.capitalize()) for state in country_states]
            states_list.append((country.name, country.name.capitalize()))

            countries.append(
                (
                    country.name.capitalize(),
                    states_list if len(states_list) > 0 else [(country.name, country.name.capitalize())],
                )
            )
        return countries

    start_date = forms.DateField(
        label="Start Date",
        required=False,
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={"type": "date"},
        ),
    )
    end_date = forms.DateField(
        label="End Date",
        required=False,
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={"type": "date"},
        ),
    )

    origin = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={"class": "form-select selectpicker", "data-live-search": "true", "id": "origin"}
        ),
        required=False,
    )

    destination = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={"class": "form-select selectpicker", "data-live-search": "true", "id": "destination"}
        ),
        required=False,
    )

    organisation = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={"class": "form-select selectpicker", "data-live-search": "true", "id": "organisation"}
        ),
        required=False,
    )

    factory_farm = forms.MultipleChoiceField(
        label="Factory / Farm",
        widget=forms.SelectMultiple(
            attrs={"class": "form-select selectpicker", "data-live-search": "true", "id": "factory_farm"}
        ),
        required=False,
    )

    immigration_status = forms.MultipleChoiceField(
        label="Immigration Status",
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select selectpicker",
                "data-live-search": "true",
                "id": "immigration_status",
            }
        ),
        required=False,
    )


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label="Start Date",
        required=True,
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "type": "date",
                "class": "form-control",
            },
        ),
    )
    end_date = forms.DateField(
        label="End Date",
        required=True,
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "type": "date",
                "class": "form-control",
            },
        ),
    )
