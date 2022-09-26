import re
from datetime import datetime, timedelta

import pandas as pd
from common.base import exclude_cols
from django import forms
from django.db import models
from pytz import country_names

from .models import Factory, JGWCache, Scheme


def get_start_date(days, format="%Y-%m-%d"):
    target_date = datetime.today() - timedelta(days=days)
    return target_date.strftime(format)


def camelCase_to_spaceDelimited(text: str):
    return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", text)


DEST_COUNTRIES = {"": "Select a Country"}
ORIGIN_COUNTRIES = {"": "Select a Country"}
FACTORIES = {"": "Select a factory or farm"}


DEST_COUNTRIES.update(
    {country_names[k].lower(): country_names[k] for k in ("MY", "QA", "SA", "AE", "GB", "PL")}
)
CATEGORIES = ["preferences"]  # , "inline", "messaging", "help_contacts"]
TIME_RANGE = {
    get_start_date(days=30): "30 Days",
    get_start_date(days=60): "60 Days",
    get_start_date(days=90): "90 Days",
    "all_time": "All Time",
}


class DependentChoiceField(forms.ChoiceField):
    def valid_value(self, value) -> bool:
        """Check to see if the provided value is a valid choice."""
        text_value = str(value)
        lower_names = [i.lower() for i in country_names.values()]
        possible_origins = {i: i for i in lower_names}
        for k, v in possible_origins.items():
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
    time_range = forms.ChoiceField(
        label="Time Range",
        choices=TIME_RANGE.items(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-2", "id": "time_range"}),
    )


class ExportReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control mx-2"

    CATEGORY = models.TextChoices("Category", " ".join(CATEGORIES))
    category = forms.ChoiceField(choices=CATEGORY.choices)
    start_date = forms.DateField(
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "placeholder": "Select a date",
                "type": "date",
                "value": "2022-06-01",
            },
        )
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "placeholder": "Select a date",
                "type": "date",
                "value": datetime.now().strftime("%Y-%m-%d"),
            },
        )
    )


class InlineQnsForm(FilterForm):
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        inline_cache = JGWCache.objects.filter(category="inline").first()
        if inline_cache is not None:
            df = pd.read_json(inline_cache.data, orient="records")
            question_list = [i for i in df.columns if i not in exclude_cols]
            question_choices = [(i, camelCase_to_spaceDelimited(i)) for i in question_list]
            question_choices = [("", "Select a question key"), *question_choices]
            self.fields["question"].choices = question_choices

    question = forms.ChoiceField(
        label="Question Key",
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-2", "id": "question"}),
    )
