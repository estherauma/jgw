import re
from datetime import datetime
from operator import itemgetter

from django import forms
from django.utils.safestring import mark_safe
from pytz import country_names

from common.inline import Inline
from common.reports import get_start_date
from common.retrieve_data import exclude_cols

from .models import Factory, Scheme


def camelCase_to_spaceDelimited(text: str):
    return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", text)

TODAY = datetime.today().date()
ORIGIN_COUNTRIES_template = {"": "Select a Country"}
ORIGIN_COUNTRIES = ORIGIN_COUNTRIES_template.copy()
ORIGIN_COUNTRIES.update({country_names[i].title(): country_names[i].title() for i in country_names})

DEST_COUNTRIES = {"": "Select a Country"}
DEST_COUNTRIES.update(
    {country_names[k].title(): country_names[k] for k in ("MY", "QA", "SA", "AE", "GB", "PL", "RO")}
)

FACTORIES = {"": "Select a Factory or Farm"}
OPERATORS = {
    "": "Select an Organisation",
    "Seasonal  Worker Scheme - Concordia": "Concordia",
    "Seasonal Worker Scheme - AG Recruitment": "AG Recruitment",
    "Seasonal Worker Scheme - Generic": "Generic",
    "Seasonal Worker Scheme - Pro-Force": "Pro-Force",
    "Seasonal Worker Scheme - Fruitful Jobs": "Fruitful Jobs",
}
CATEGORIES = {
    "preferences": "Demographics",
    "chapters": "Chapters",
    "inlineQNs_participation": "InlineQuestions Participation",
    "inlineQNs_responses": "InlineQuestions Response Breakdown",
}
TIME_RANGE = {
    "": "Select a time range.",
    get_start_date(days=30): "30 Days",
    get_start_date(days=60): "60 Days",
    get_start_date(days=90): "90 Days",
    "all_time": "All Time",
}


class DependentChoiceField(forms.ChoiceField):
    def valid_value(self, value) -> bool:
        """Check to see if the provided value is a valid choice."""
        text_value = str(value)
        _names = [i.title() for i in country_names.values()]
        possible_origins = {i: i for i in _names}
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
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for f in self.fields:
            if f not in ("start_date", "end_date", "time_range", "destination", "scheme_name"):
                self.fields[f].widget.attrs = {
                    "onChange": mark_safe("filterData();"),
                    "class": "form-select mx-1",
                    "id": f,
                }

    def clean(self):
        cleaned_data = super().clean()
        start_date, end_date, time_range = itemgetter("start_date", "end_date", "time_range")(cleaned_data)

        if (start_date or end_date) and time_range:
            raise forms.ValidationError("Please fill either start/end date or time range, but not both!")

        if all((start_date, end_date)) and start_date > end_date:
            raise forms.ValidationError("Start date must be earlier than end date!")

        return cleaned_data

    destination = forms.ChoiceField(
        choices=DEST_COUNTRIES.items(),
        required=False,
        widget=forms.Select(
            attrs={"class": "form-select mx-1", "id": "destination", "onChange": "getOriginOptions();"}
        ),
    )
    origin = DependentChoiceField(choices=ORIGIN_COUNTRIES.items(), required=False)
    scheme_name = forms.ModelChoiceField(
        label="Scheme",
        required=False,
        queryset=Scheme.objects.all(),
        widget=forms.Select(
            attrs={"class": "form-select mx-1", "id": "scheme_name", "onChange": "getFactoryOptions();"}
        ),
    )
    organisation = forms.ChoiceField(label="Organisation", choices=OPERATORS.items(), required=False)
    factory_farm = forms.ModelChoiceField(
        label="Factory/Farm", required=False, queryset=Factory.objects.all()
    )
    time_range = forms.ChoiceField(
        label="Time Range",
        choices=TIME_RANGE.items(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select mx-1",
                "id": "time_range",
                "onChange": mark_safe(
                    """
                    document.getElementById('start_date').value = '';
                    document.getElementById('end_date').value = '';
                    filterData()
                """
                ),
            }
        ),
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "class": "form-control mx-1",
                "id": "start_date",
                "placeholder": "Select a date",
                "type": "date",
                "max": TODAY,
            },
        ),
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "class": "form-control mx-1",
                "id": "end_date",
                "placeholder": "Select a date",
                "type": "date",
                "max": TODAY,
            },
        ),
    )


class ExportReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control mx-1"

    category = forms.ChoiceField(choices=CATEGORIES.items())
    start_date = forms.DateField(
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={"placeholder": "Select a date", "type": "date", "value": "2022-06-01"},
        )
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "placeholder": "Select a date",
                "type": "date",
                "value": TODAY,
            },
        )
    )


class InlineQnsForm(FilterForm):
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        helper = Inline()
        df = helper.get_df()
        question_list = [i for i in df.columns if i not in exclude_cols]
        question_choices = [(i, camelCase_to_spaceDelimited(i)) for i in question_list]
        question_choices = [("", "Select a question key"), *question_choices]
        self.fields["question"].choices = question_choices
        qn_mark = mark_safe("'")
        form_name = f"{qn_mark}filter_form{qn_mark}"
        for f in self.fields:
            if f not in ("start_date", "end_date", "time_range"):
                self.fields[f].widget.attrs = {
                    "onChange": mark_safe("document.getElementById('filter_form').submit();"),
                    "class": "form-select mx-1",
                    "id": f,
                }

    question = forms.ChoiceField(
        label="Question Key",
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-1", "id": "question"}),
    )


class AppEventsForm(forms.Form):
    TIME_RANGE = {
        "7 Days": "7 Days",
        "30 Days": "30 Days",
        "60 Days": "60 Days",
        # "90 Days": "90 Days",
    }
    time_range = forms.ChoiceField(
        label="Time Range",
        choices=TIME_RANGE.items(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select mx-1", "id": "time_range"}),
    )
