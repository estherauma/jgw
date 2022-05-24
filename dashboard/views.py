from operator import itemgetter
from typing import Dict

from common.help_contacts import HelpContacts
from common.inline import Inline
from common.messaging import Messaging
from common.preferences import Preferences
from common.retrieve_data import FILENAMES, JGWApi
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from pytz import country_names
from requests.exceptions import HTTPError

from .forms import ORIGIN_COUNTRIES, FilterForm


def form_chart_data(data: Dict) -> Dict:
    """
    reshapes data to shape expected by chart library
    """
    return {i: {"labels": list(data[i].keys()), "data": list(data[i].values())} for i in data.keys()}


@login_required()
def preferences_stats(request):
    if request.method == "POST":
        form = FilterForm(request.POST)
        if form.is_valid():
            filters = form.cleaned_data.copy()
            return redirect(reverse("dashboard:preferences") + "?" + urlencode(filters))
        return render(request, "preferences.html", context={"form": form})
    filters = None or request.GET
    if filters is not None:
        filters = {k: v for k, v in filters.items() if bool(v)}
    form = FilterForm(initial=filters)
    try:
        pref = Preferences()
        _data = pref.get_stats_object(filters=filters)
        chart_data = form_chart_data(_data)
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
    except HTTPError as err:
        messages.error(request, "Error fetching data!")
        return render(request, "preferences.html", context={"form": form})
    return render(request, "preferences.html", context={"data": chart_data, "form": form, "filter_string": urlencode(filters)})


@login_required()
def inline_question_stats(request):
    if request.method == "POST":
        form = FilterForm(request.POST)
        if form.is_valid():
            filters = form.cleaned_data.copy()
            return redirect(reverse("dashboard:inline") + "?" + urlencode(filters))
        return render(request, "inline.html", context={"form": form})
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
        context={"data": chart_data, "form": form, "response_count": response_count, "filter_string": urlencode(filters)},
    )


@login_required()
def messaging_question_stats(request):
    if request.method == "POST":
        form = FilterForm(request.POST)
        if form.is_valid():
            filters = form.cleaned_data.copy()
            return redirect(reverse("dashboard:messaging") + "?" + urlencode(filters))
        return render(request, "messaging.html", context={"form": form})
    filters = None or request.GET
    if filters is not None:
        filters = {k: v for k, v in filters.items() if bool(v)}
    form = FilterForm(initial=filters)
    try:
        msg_responses = Messaging()
        _data = msg_responses.get_stats_object(filters=filters)
        chart_data = form_chart_data(_data)
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
    except HTTPError:
        messages.error(request, "Error fetching data!")
        return render(request, "messaging.html", context={"form": form})
    return render(request, "messaging.html", context={"data": chart_data, "form": form, "filter_string": urlencode(filters)})


@login_required()
def help_contacts_stats(request):
    if request.method == "POST":
        form = FilterForm(request.POST)
        if form.is_valid():
            filters = form.cleaned_data.copy()
            return redirect(reverse("dashboard:help_contacts") + "?" + urlencode(filters))
        return render(request, "help_contacts.html", context={"form": form})
    filters = None or request.GET
    if filters is not None:
        filters = {k: v for k, v in filters.items() if bool(v)}
    form = FilterForm(initial=filters)
    try:
        help_contacts_stats = HelpContacts()
        _data = help_contacts_stats.get_stats_object(filters=filters)
        chart_data = form_chart_data(_data)
        if not any(bool(i) for i in _data.values()):
            messages.error(request, "No data matches this search!")
    except HTTPError:
        messages.error(request, "Error fetching data!")
        return render(request, "help_contacts.html", context={"form": form})
    return render(request, "help_contacts.html", context={"data": chart_data, "form": form, "filter_string": urlencode(filters)})


@login_required()
def process_filter_options(request):
    filters = request.GET
    filters = {k: v for k, v in filters.items() if bool(v)}
    pref = Preferences()
    df = pref.get_df(filters)
    origins = set([i.split(" -> ")[0] for i in df["route"].tolist()])
    _country_names = {v.lower(): k for k, v in country_names.items()}
    ORIGIN_COUNTRIES.update({_country_names.get(k): k for k in origins})
    return JsonResponse(ORIGIN_COUNTRIES)


@login_required()
def export_to_excel_file(request, key):
    helpers = {
        "inline": Inline(),
        "preferences": Preferences(),
        "help_contacts": HelpContacts(),
        "messaging": Messaging(),
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
