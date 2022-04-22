from operator import itemgetter
from typing import Dict

from common.inline import Inline
from common.preferences import Preferences
from common.retrievedata import JGWApi
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlencode

from .forms import FilterForm


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
            filters["destination"] = ",".join(filters["destination"])
            return redirect(reverse("dashboard:index") + "?" + urlencode(filters))

    form = FilterForm()
    filters = None or request.GET
    pref = Preferences()
    _data = pref.get_stats_object(filters=filters)
    chart_data = form_chart_data(_data)
    if not any(bool(i) for i in _data.values()):
        messages.error(request, "No data matches this search!")
    return render(request, "dashboard.html", context={"data": chart_data, "form": form})


@login_required()
def inline_question_stats(request):
    if request.method == "POST":
        form = FilterForm(request.POST)
        if form.is_valid():
            filters = form.cleaned_data.copy()
            filters["destination"] = ",".join(filters["destination"])
            return redirect(reverse("dashboard:inline_question_stats") + "?" + urlencode(filters))

    form = FilterForm()
    filters = None or request.GET
    inline_responses = Inline()
    _data = inline_responses.get_stats_object(filters=filters)
    response_count, _data = itemgetter("response_count", "data")(_data)
    chart_data = form_chart_data(_data)
    if not any(bool(i) for i in _data.values()):
        messages.error(request, "No data matches this search!")

    return render(
        request,
        "inline.html",
        context={"data": chart_data, "form": form, "response_count": response_count},
    )


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
