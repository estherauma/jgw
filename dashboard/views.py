from operator import itemgetter
from typing import Dict

from common.help_contacts import HelpContacts
from common.inline import Inline
from common.messaging import Messaging
from common.preferences import Preferences
from common.retrieve_data import JGWApi
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
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
            return redirect(reverse("dashboard:index") + "?" + urlencode(filters))
        return render(request, "dashboard.html", context={"form": form})
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
        return render(request, "dashboard.html", context={"form": form})
    return render(request, "dashboard.html", context={"data": chart_data, "form": form})


@login_required()
def inline_question_stats(request):
    if request.method == "POST":
        form = FilterForm(request.POST)
        if form.is_valid():
            filters = form.cleaned_data.copy()
            return redirect(reverse("dashboard:inline_question_stats") + "?" + urlencode(filters))
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
    except HTTPError as err:
        messages.error(request, "Error fetching data!")
        return render(request, "inline.html", context={"form": form})
    return render(
        request,
        "inline.html",
        context={"data": chart_data, "form": form, "response_count": response_count},
    )


@login_required()
def messaging_question_stats(request):
    if request.method == "POST":
        form = FilterForm(request.POST)
        if form.is_valid():
            filters = form.cleaned_data.copy()
            return redirect(reverse("dashboard:messaging_question_stats") + "?" + urlencode(filters))
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
    return render(request, "messaging.html", context={"data": chart_data, "form": form})


@login_required()
def help_contacts_stats(request):
    if request.method == "POST":
        form = FilterForm(request.POST)
        if form.is_valid():
            filters = form.cleaned_data.copy()
            return redirect(reverse("dashboard:help_contacts_stats") + "?" + urlencode(filters))
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
    return render(request, "help_contacts.html", context={"data": chart_data, "form": form})


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
def retrieve_preferences(request):
    api = JGWApi()
    api.get_preferences()


@login_required()
def export_preferences(request):
    preference = Preferences()
    results = preference.get_dataframe()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=preferences_export.csv"
    results.to_csv(path_or_buf=response, sep=";", float_format="%.2f", index=False, decimal=",")
    return response


@login_required()
def export_inline(request):
    inline = Inline()
    results = inline.get_dataframe()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=inline_export.csv"
    results.to_csv(path_or_buf=response, sep=";", float_format="%.2f", index=False, decimal=",")
    return response


def test_sentry(request):
    division_error = 1 / 0
