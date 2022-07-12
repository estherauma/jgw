from operator import itemgetter
from typing import Dict
from unicodedata import category

import pandas as pd
from common.checklists import CheckLists
from common.help_contacts import HelpContacts
from common.inline import Inline
from common.messaging import Messaging
from common.preferences import Preferences
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from pytz import country_names
from requests.exceptions import HTTPError

from .forms import FACTORIES, ORIGIN_COUNTRIES, ExportReportForm, FilterForm

HELPERS = {
    "inline": lambda: Inline(),
    "preferences": lambda: Preferences(),
    "help_contacts": lambda: HelpContacts(),
    "messaging": lambda: Messaging(),
    "visa": lambda: CheckLists(key="visa"),
    "joboffer": lambda: CheckLists(key="joboffer"),
    "contract": lambda: CheckLists(key="contract"),
    "beforeyougo": lambda: CheckLists(key="beforeyougo"),
}
KEYS = ["age", "locale", "gender", "origin", "destination", "organisation", "language"]
OPERATORS = {
    "concordia": "Seasonal  Worker Scheme - Concordia",
    "ag_recruitment": "Seasonal  Worker Scheme - AG Recruitment",
    "generic": "Seasonal  Worker Scheme - Generic",
    "pro_force": "Seasonal  Worker Scheme - Pro-Force",
}


def form_chart_data(data: Dict) -> Dict:
    """
    reshapes data to shape expected by chart library
    """
    return {i: {"labels": list(data[i].keys()), "data": list(data[i].values())} for i in data.keys()}


def process_filters(request):
    user = request.user
    filters = {} or request.GET
    role_filters = {
        "Scheme": {"scheme_name": user.scheme},
        "Factory": {"factory_farm": user.factory},
    }
    filters.update(role_filters.get(user.role, {}))
    if bool(filters):
        filters = {k: v for k, v in filters.items() if bool(v)}
    return filters


def redirect_to_filtered_data(request, url, template_name):
    form = FilterForm(request.POST)
    if form.is_valid():
        filters = form.cleaned_data.copy()
        # urlencode does not support NoneType values
        filters = {k: ("" if v is None else v) for k, v in filters.items()}
        return redirect(f"{url}?{urlencode(filters)}")
    return render(request, template_name, context={"form": form})


def render_data(request, template_name, helper):
    filters = process_filters(request)

    form = FilterForm(initial=filters)
    try:
        _data = helper.get_stats_object(filters=filters)
        chart_data = form_chart_data(_data)
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
    except HTTPError:
        messages.error(request, "Error fetching data!")
        return render(request, template_name, context={"form": form})
    return render(
        request,
        template_name,
        context={"data": chart_data, "form": form, "filter_string": urlencode(filters)},
    )


def get_count_series(df: pd.DataFrame, key: str) -> pd.Series:
    return df[key].value_counts()


def write_to_xls_sheet(df: pd.DataFrame, sheet_name: str, filename: str):
    with pd.ExcelWriter(filename, mode="a", if_sheet_exists="overlay") as writer:
        startrow = 0
        for key in KEYS:
            count = get_count_series(df, key)
            count.to_excel(writer, sheet_name=sheet_name, startcol=0, startrow=startrow)
            startrow += count.size + 1


def get_report(start, end, category):
    filename = f"jgwpandas/static/assets/data/{category}.xlsx"
    df = pd.read_excel(filename)
    df = df.loc[df["createdAt"].between(start, end, inclusive=True)]
    write_to_xls_sheet(df, sheet_name="Pref-All", filename=f"{category}.xlsx")
    for k, operator_name in OPERATORS.items():
        new_df = df.loc[df["organisation"] == operator_name]
        new_df = new_df.loc[~new_df["origin"].isin(["MY", "US", "KY", "UG", "TZ", "BD"])]
        write_to_xls_sheet(new_df, sheet_name=f"pref-{k}", filename=f"{category}.xlsx")
    return f"category.xlsx"


@login_required()
def preferences_stats(request):
    if request.method == "POST":
        return redirect_to_filtered_data(
            request, url=reverse("dashboard:preferences"), template_name="preferences.html"
        )
    return render_data(request, template_name="preferences.html", helper=Preferences())


@login_required()
def messaging_question_stats(request):
    if request.method == "POST":
        return redirect_to_filtered_data(
            request, url=reverse("dashboard:messaging"), template_name="messaging.html"
        )
    return render_data(request, template_name="messaging.html", helper=Messaging())


@login_required()
def help_contacts_stats(request):
    if request.method == "POST":
        return redirect_to_filtered_data(
            request, url=reverse("dashboard:help_contacts"), template_name="help_contacts.html"
        )
    return render_data(request, template_name="help_contacts.html", helper=HelpContacts())


@login_required()
def checklists_stats(request, key):
    if request.method == "POST":
        return redirect_to_filtered_data(
            request, url=reverse("dashboard:checklists", args=(key,)), template_name=f"{key}_checklists.html"
        )
    return render_data(request, template_name=f"{key}_checklists.html", helper=CheckLists(key=key))


@login_required()
def inline_question_stats(request):
    if request.method == "POST":
        return redirect_to_filtered_data(
            request, url=reverse("dashboard:inline"), template_name="inline.html"
        )
    filters = process_filters(request)
    form = FilterForm(initial=filters)
    try:
        inline_responses = Inline()
        _data = inline_responses.get_stats_object(filters=filters)
        response_count, _data = itemgetter("response_count", "data")(_data)
        chart_data = form_chart_data(_data)
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
    except HTTPError:
        messages.error(request, "Error fetching data!")
        return render(request, "inline.html", context={"form": form})
    return render(
        request,
        "inline.html",
        context={
            "data": chart_data,
            "form": form,
            "response_count": response_count,
            "filter_string": urlencode(filters),
        },
    )


@login_required()
def process_origin_options(request, key):
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    helper = HELPERS.get(key)
    helper = helper()
    df = helper.get_df(filters)
    origins = df["origin"][df["origin"].notna()]
    origins = set(origins.tolist())
    origin_countries = ORIGIN_COUNTRIES.copy()
    origin_countries.update({k: country_names.get(k) for k in origins})
    return JsonResponse(origin_countries)


@login_required()
def process_factory_options(request, key):
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    helper = HELPERS.get(key)
    helper = helper()
    df = helper.get_df(filters)
    if "factoryFarm" in df.columns:
        factories = FACTORIES.copy()
        factories.update({k: k for k in set(df["factoryFarm"].tolist())})
    return JsonResponse(factories)


@login_required()
def export_to_excel_file(request, key):
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    helper = HELPERS[key]
    helper = helper()
    df = helper.get_df(filters)
    if filename is None:
        messages.error(request, "Failed to export!")
        return redirect(reverse(f"dashboard:{key}"))
    filename = helper.get_df_path(filters, extension="xlsx")
    df.to_excel(filename, index=False)
    response = FileResponse(open(filename, "rb"))
    return response


def export_report(request):
    form = ExportReportForm()
    if request.method == "POST":
        form = ExportReportForm(request.POST)
        if form.is_valid():
            start, end, category = itemgetter("start_date", "end_date", "category")(form.cleaned_data)
            filename = get_report(start, end, category)
            response = FileResponse(open(filename, "rb"))
            return response
        else:
            messages.error(request, "Error validating form!")
    return render(request, "batch_export.html", context={"form": form})


def test_sentry(request):
    division_error = 1 / 0
