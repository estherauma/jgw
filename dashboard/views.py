import shutil
from datetime import datetime
from operator import itemgetter
from typing import Dict

import pandas as pd
from common.app_events import AppEvents
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
from requests.exceptions import HTTPError

from .forms import (
    FACTORIES,
    ORIGIN_COUNTRIES,
    AppEventsForm,
    ExportReportForm,
    FilterForm,
    InlineQnsForm,
    get_start_date,
)
from .models import JGWCache

KEYS = ["age", "locale", "gender", "origin", "destination", "organisation", "language"]
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
OPERATORS = {
    "concordia": "Seasonal  Worker Scheme - Concordia",
    "ag_recruitment": "Seasonal Worker Scheme - AG Recruitment",
    "generic": "Seasonal Worker Scheme - Generic",
    "pro_force": "Seasonal Worker Scheme - Pro-Force",
    "fruitful": "Seasonal Worker Scheme - Fruitful Jobs",
}


def form_chart_data(data: Dict) -> Dict:
    """
    reshapes data as expected by chart library
    """
    return {i: {"labels": list(data[i].keys()), "data": list(data[i].values())} for i in data.keys()}


def process_filters(request):
    user = request.user
    role_filters = {
        "Scheme": {"scheme_name": user.scheme},
        "Factory": {"factory_farm": user.factory},
    }
    filters = request.GET.dict()
    filters.update(role_filters.get(user.role, {}))
    if bool(filters):
        filters = {k: v for k, v in filters.items() if bool(v)}
        if "time_range" not in filters:
            filters["time_range"] = get_start_date(days=30)
    else:
        filters["time_range"] = get_start_date(days=30)
    return filters


def redirect_to_filtered_data(request, url, template_name, form=None):
    form = form if form is not None else FilterForm(request.POST)
    if form.is_valid():
        filters = form.cleaned_data.copy()
        # urlencode does not support NoneType values
        filters = {k: v for k, v in filters.items() if v not in [None, ""]}
        return redirect(f"{url}?{urlencode(filters)}")
    return render(request, template_name, context={"form": form})


def render_data(request, template_name, helper):
    filters = process_filters(request)
    form = FilterForm(initial=filters)
    context_data = {"form": form}
    try:
        _data = helper.compute_stats(filters=filters)
        chart_data = form_chart_data(_data)
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
    except HTTPError:
        messages.error(request, "Error fetching data!")
        return render(request, template_name, context={"form": form})
    context_data.update({"data": chart_data, "filter_string": urlencode(filters)})
    if helper.cleaned is False:
        messages.info(
            request,
            (
                "Raw data is shown while we finish processing your results."
                "\nRefresh after a few minutes to view the completed stats."
            ),
        )
    return render(request, template_name, context=context_data)


@login_required()
def inline_question_stats(request):
    filters = process_filters(request)
    form = InlineQnsForm(initial=filters)
    context_data = {"form": form}
    chart_data = None
    if request.method == "POST":
        return redirect_to_filtered_data(
            request,
            url=reverse("dashboard:inline"),
            template_name="inline.html",
            form=InlineQnsForm(request.POST),
        )
    try:
        inline_responses = Inline()
        _data = inline_responses.compute_stats(filters=filters)
        response_count, _data = itemgetter("response_count", "data")(_data)
        chart_data = form_chart_data(_data)
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
    except HTTPError:
        messages.error(request, "Error fetching data!")
        return render(request, "inline.html", context={"form": form})
    context_data.update(
        {"data": chart_data, "response_count": response_count, "filter_string": urlencode(filters)}
    )
    if inline_responses.cleaned is False:
        messages.info(
            request,
            (
                "Raw data is shown while we finish processing your results."
                "\nRefresh after a few minutes to view the completed stats."
            ),
        )
    return render(request, "inline.html", context=context_data)


@login_required()
def app_events_stats(request):
    helper = AppEvents()
    context_data = {}
    template_name = "app_events.html"
    filters = request.GET.dict() or {}
    if "time_range" not in filters:
        filters["time_range"] = "7 Days"

    def reformat_grouped_data(data):
        counts = [i["Count"] for i in data]
        users = [i["Users"] for i in data]
        return [
            {"label": "Counts", "backgroundColor": "blue", "data": counts},
            {"label": "Users", "backgroundColor": "red", "data": users},
        ]

    if request.method == "POST":
        return redirect_to_filtered_data(
            request,
            url=reverse("dashboard:app_events"),
            template_name="app_events.html",
            form=AppEventsForm(request.POST),
        )
    try:
        _data = helper.compute_stats()
        chart_data = form_chart_data(_data)
        chart_data["chapters"]["data"] = reformat_grouped_data(chart_data["chapters"]["data"])
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
    except HTTPError:
        messages.error(request, "Error fetching data!")
        return render(request, template_name)
    context_data.update({"data": chart_data})
    if helper.cleaned is False:
        messages.info(
            request,
            (
                "Raw data is shown while we finish processing your results."
                "\nRefresh after a few minutes to view the completed stats."
            ),
        )
    return render(request, template_name, context=context_data)


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
def process_origin_options(request, key):
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    helper = HELPERS.get(key)
    helper = helper()
    df = helper.get_df(filters)
    origins = df["origin"][df["origin"].notna()]
    origins = set(origins.tolist())
    origin_countries = ORIGIN_COUNTRIES.copy()
    origin_countries.update({k: k.title() for k in origins})
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
    filters = process_filters(request)
    helper = HELPERS[key]
    helper = helper()
    df = helper.get_df(filters)
    filename = helper.get_df_path(filters, extension="xlsx")
    if filename is None:
        messages.error(request, "Failed to export!")
        return redirect(reverse(f"dashboard:{key}"))
    df.to_excel(filename, index=False)
    response = FileResponse(open(filename, "rb"))
    return response


def count_unique_series(df: pd.DataFrame, key: str) -> pd.Series:
    return df[key].value_counts()


def write_to_xls_sheet(df: pd.DataFrame, sheet_name: str, filename: str):
    with pd.ExcelWriter(filename, mode="a", if_sheet_exists="overlay") as writer:
        startrow = 0
        for key in KEYS:
            count = count_unique_series(df, key)
            count.to_excel(writer, sheet_name=sheet_name, startcol=0, startrow=startrow)
            startrow += count.size + 1


def get_report(start, end, category):
    output_filename = f"{category}.xlsx"
    result = JGWCache.objects.filter(category=category, date_created=datetime.today().date()).first()
    df = pd.read_json(result.data, orient="records")
    df = df.loc[df["createdAt"].between(start, end, inclusive="both")]
    try:
        write_to_xls_sheet(df, sheet_name="Pref-All", filename=output_filename)
    except FileNotFoundError:
        shutil.copy("./temp/preferences.xlsx", "./preferences.xlsx")
        write_to_xls_sheet(df, sheet_name="Pref-All", filename=output_filename)
    for k, operator_name in OPERATORS.items():
        new_df = df.loc[df["organisation"] == operator_name]
        new_df = new_df.loc[~new_df["origin"].isin(["MY", "US", "KY", "UG", "TZ", "BD"])]
        write_to_xls_sheet(new_df, sheet_name=f"pref-{k}", filename=output_filename)
    return output_filename


@login_required()
def export_report(request):
    form = ExportReportForm()
    if request.method == "POST":
        form = ExportReportForm(request.POST)
        if form.is_valid():
            start, end, category = itemgetter("start_date", "end_date", "category")(form.cleaned_data)
            start, end = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
            filename = get_report(start, end, category)
            response = FileResponse(open(filename, "rb"))
            return response
        else:
            messages.error(request, "Error validating form!")
    return render(request, "batch_export.html", context={"form": form})


def test_sentry(request):
    division_error = 1 / 0
