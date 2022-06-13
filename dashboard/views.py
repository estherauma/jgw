from operator import itemgetter
from typing import Dict

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

from .forms import FACTORIES, ORIGIN_COUNTRIES, FilterForm


def form_chart_data(data: Dict) -> Dict:
    """
    reshapes data to shape expected by chart library
    """
    return {i: {"labels": list(data[i].keys()), "data": list(data[i].values())} for i in data.keys()}


def redirect_to_filtered_data(request, url, template_name):
    form = FilterForm(request.POST)
    if form.is_valid():
        filters = form.cleaned_data.copy()
        return redirect(f"{url}?{urlencode(filters)}")
    return render(request, template_name, context={"form": form})


def render_data(request, template_name, helper):
    filters = None or request.GET
    if filters is not None:
        filters = {k: v for k, v in filters.items() if bool(v)}
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
    filters = None or request.GET
    if filters is not None:
        filters = {k: v for k, v in filters.items() if bool(v)}
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
    helpers = {
        "inline": Inline(),
        "preferences": Preferences(),
        "help_contacts": HelpContacts(),
        "messaging": Messaging(),
    }
    helper = helpers.get(key)
    df = helper.get_df(filters)
    origins = set([i.split(" -> ")[0] for i in df["route"].tolist()])
    _country_names = {v.lower(): k for k, v in country_names.items()}
    ORIGIN_COUNTRIES.update({_country_names.get(k): k for k in origins})
    return JsonResponse(ORIGIN_COUNTRIES)


@login_required()
def process_factory_options(request, key):
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    helpers = {
        "inline": Inline(),
        "preferences": Preferences(),
        "help_contacts": HelpContacts(),
        "messaging": Messaging(),
    }
    helper = helpers.get(key)
    df = helper.get_df(filters)
    if "factoryFarm" in df.columns:
        FACTORIES.update({k: k for k in set(df["factoryFarm"].tolist())})
    return JsonResponse(FACTORIES)


@login_required()
def export_to_excel_file(request, key):
    helpers = {
        "inline": Inline(),
        "preferences": Preferences(),
        "help_contacts": HelpContacts(),
        "messaging": Messaging(),
        "visa": CheckLists(key="visa"),
        "joboffer": CheckLists(key="joboffer"),
        "contract": CheckLists(key="contract"),
        "beforeyougo": CheckLists(key="beforeyougo"),
    }
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    helper = helpers[key]
    df = helper.get_df(filters)
    filename = helper.get_df_path(filters, extension="xlsx")
    df.to_excel(filename, index=False)

    if filename is None:
        messages.error(request, "Failed to export!")
        return redirect(reverse(f"dashboard:{key}"))
    response = FileResponse(open(filename, "rb"))
    return response


def test_sentry(request):
    division_error = 1 / 0
