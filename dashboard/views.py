from datetime import datetime
from http import HTTPStatus
from operator import itemgetter
from typing import Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import FileResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from requests.exceptions import HTTPError

from common.app_events import AppEvents
from common.checklists import CheckLists
from common.help_contacts import HelpContacts
from common.inline import Inline
from common.messaging import Messaging
from common.preferences import Preferences
from common.reports import get_start_date, get_SWS_report

from .forms import (
    FACTORIES,
    AppEventsForm,
    ExportReportForm,
    FilterForm,
    InlineQnsForm,
    ORIGIN_COUNTRIES_template,
    get_start_date,
)

KEYS = ["age", "locale", "gender", "origin", "destination", "organisation", "language"]
HELPERS = {
    "inline": lambda: Inline(),
    "inlineQNs_responses": lambda: Inline(),
    "inlineQNs_participation": lambda: Inline(),
    "preferences": lambda: Preferences(),
    "help_contacts": lambda: HelpContacts(),
    "messaging": lambda: Messaging(),
    "visa": lambda: CheckLists(key="visa"),
    "joboffer": lambda: CheckLists(key="joboffer"),
    "contract": lambda: CheckLists(key="contract"),
    "beforeyougo": lambda: CheckLists(key="beforeyougo"),
}
OPERATORS = {
    "Concordia": "Seasonal  Worker Scheme - Concordia",
    "AG Recruitment": "Seasonal Worker Scheme - AG Recruitment",
    "Generic": "Seasonal Worker Scheme - Generic",
    "Pro-Force": "Seasonal Worker Scheme - Pro-Force",
    "Fruitful Jobs": "Seasonal Worker Scheme - Fruitful Jobs",
}
TODAY = datetime.today().strftime("%Y-%m-%d")


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
    return filters


def redirect_to_filtered_data(request, url, template_name, form=None):
    """Turns filter form values into query args for view at base url to filter data"""
    form = form if form is not None else FilterForm(request.POST)
    if form.is_valid():
        filters = form.cleaned_data.copy()
        filters = {k: v for k, v in filters.items() if bool(v)}  # urlencode does not support NoneType values
        return redirect(f"{url}?{urlencode(filters)}")
    return render(request, template_name, context={"form": form})


def format_time_range(filters):
    fields = filters.keys()
    if "time_range" not in fields and "start_date" not in fields:
        # set time-range to 30 if no time-range/date
        filters["time_range"] = f"{get_start_date(days=30)},{TODAY}"
    elif "time_range" in fields:
        filters["time_range"] = f"{filters['time_range']},{TODAY}"
    elif ("end_date" in fields or "start_date" in fields) and "time_range" not in fields:
        filters["time_range"] = f"{filters['start_date']},{filters.get('end_date', TODAY)}"
    return filters


def get_filters_from_form(form):
    if form.is_valid():
        form_data = form.cleaned_data.copy()
        filters = {k: v for k, v in form_data.items() if bool(v)}
    else:
        raise ValidationError(message=dict(form.errors))
    return filters


def get_user_role(user):
    role_filters = {
        "Scheme": {"scheme_name": user.scheme},
        "Factory": {"factory_farm": user.factory},
    }
    return role_filters.get(user.role, {})


def filter_data(request, category):
    form = InlineQnsForm(request.POST) if category == "inline" else FilterForm(request.POST)
    helper = HELPERS[category]()
    try:
        filters = get_filters_from_form(form)
        filters.update(get_user_role(request.user))
        filters = format_time_range(filters)

        data = helper.compute_stats(filters=filters)
        if category == "inline":
            response_count, raw_chart_data = itemgetter("response_count", "data")(data)
            chart_data = form_chart_data(raw_chart_data)
            return JsonResponse({"chart_data": chart_data, "response_count": response_count})
        chart_data = form_chart_data(data)
    except ValidationError as e:
        return JsonResponse({"form_errors": e.message_dict}, status=HTTPStatus.BAD_REQUEST)
    return JsonResponse(chart_data)


@login_required()
def home(request):
    return render(request, template_name="dashboard/home_page.html")


@login_required()
def app_events_stats(request):
    helper = AppEvents()
    context_data = {"form": AppEventsForm()}
    template_name = "dashboard/app_events.html"
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
            template_name=template_name,
            form=AppEventsForm(request.POST),
        )
    try:
        _data = helper.compute_stats(filters=filters)
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
            return render(request, template_name, context=context_data)
        context_data["total_installs"] = _data["total_installs"]
        chart_data = form_chart_data(
            {"chapters": _data["chapters"], "chapters_feedback": _data["chapters_feedback"]}
        )
        chart_data["chapters"]["data"] = reformat_grouped_data(chart_data["chapters"]["data"])
        chart_data["chapters"]["data"] = reformat_grouped_data(chart_data["chapters_feedback"]["data"])
    except HTTPError:
        messages.error(request, "Error fetching data!")
        return render(request, template_name, context=context_data)
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
def inline_question_stats(request):
    form = InlineQnsForm(initial={"time_range": f"{get_start_date(days=30)}, {TODAY}"})
    return render(request, "dashboard/inline.html", {"form": form})


@login_required()
def preferences_stats(request):
    form = FilterForm(initial={"time_range": f"{get_start_date(days=30)}, {TODAY}"})
    return render(request, "dashboard/preferences.html", {"form": form})


@login_required()
def messaging_question_stats(request):
    form = FilterForm(initial={"time_range": f"{get_start_date(days=30)}, {TODAY}"})
    return render(request, "dashboard/messaging.html", {"form": form})


@login_required()
def help_contacts_stats(request):
    form = FilterForm(initial={"time_range": f"{get_start_date(days=30)}, {TODAY}"})
    return render(request, "dashboard/help_contacts.html", {"form": form})


@login_required()
def checklists_stats(request, key):
    form = FilterForm(initial={"time_range": f"{get_start_date(days=30)}, {TODAY}"})
    return render(request, f"dashboard/{key}_checklists.html", {"form": form})


@login_required()
def process_origin_options(request, key):
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    helper = HELPERS.get(key)
    helper = helper()
    df = helper.get_df(filters)
    origin_countries = ORIGIN_COUNTRIES_template.copy()
    if "origin" in df.columns:
        origins = df["origin"][df["origin"].notna()]
        origins = sorted(origins.unique())
        origin_countries.update({k: k for k in origins})
    return JsonResponse(origin_countries)


@login_required()
def process_factory_options(request, key):
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    helper = HELPERS.get(key)
    helper = helper()
    df = helper.get_df(filters)
    factories = FACTORIES.copy()
    if "factoryFarm" in df.columns:
        factories.update({k: k for k in sorted(df["factoryFarm"].unique())})
    return JsonResponse(factories)


@login_required()
def export_to_excel_file(request, key):
    if key not in ("preferences", "chapters", "inlineQNs_participation", "inlineQNs_responses"):
        messages.error(request, "Report not yet available!")
        return redirect(reverse("dashboard:preferences"))
    form = InlineQnsForm(request.POST) if key.startswith("inlineQNs") else FilterForm(request.POST)
    helper = HELPERS[key]()
    try:
        filters = get_filters_from_form(form)
        filters = format_time_range(filters)
        start, end = filters["time_range"].split(",")
        df = helper.get_df(filters)
        filename = get_SWS_report(start=start, end=end, category=key, df=df)
        response = FileResponse(open(filename, "rb"))
    except ValidationError as e:
        return JsonResponse({"form_errors": e.message_dict}, status=HTTPStatus.BAD_REQUEST)
    return response


@login_required()
def export_report(request):
    form = ExportReportForm()
    if request.method == "POST":
        form = ExportReportForm(request.POST)
        if form.is_valid():
            start, end, category = itemgetter("start_date", "end_date", "category")(form.cleaned_data)
            start, end = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
            filename = get_SWS_report(start, end, category)
            response = FileResponse(open(filename, "rb"))
            return response
        else:
            messages.error(request, "Error validating form!")
    return render(request, "dashboard/batch_export.html", context={"form": form})


def test_sentry(request):
    division_error = 1 / 0
