from operator import itemgetter
from typing import Dict

from common.inline import Inline
from common.preferences import Preferences
from common.retrievedata import JGWApi
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


def form_chart_data(data: Dict) -> Dict:
    """
    reshapes data to shape expected by chart library
    """
    return {i: {"labels": list(data[i].keys()), "data": list(data[i].values())} for i in data.keys()}


@login_required()
def preferences_stats(request):
    _data = Preferences().get_data_object()
    chart_data = form_chart_data(_data)
    return render(request, "dashboard.html", context={"data": chart_data})


@login_required()
def inline_question_stats(request):
    response_count, _data = itemgetter("totalResponses", "data")(Inline().get_data_object())
    chart_data = form_chart_data(_data)

    return render(
        request,
        "inline.html",
        context={"data": chart_data, "response_count": response_count},
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
