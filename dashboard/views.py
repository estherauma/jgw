from django.http import response, HttpResponse
from django.shortcuts import render
import os

from pandas.core import api
from common.inline import Inline
from common.retrievedata import JGWApi
from common.preferences import Preferences
from rest_framework.response import Response
from rest_framework.decorators import api_view




# Create your views here.
def index(request):
    return render(request, 'dashboard.html')

def inline(request):
    return render(request, 'inline.html')

def test_sentry(request):
    division_error = 1/0

def retrieve_preferences(request):
    api = JGWApi()
    api.get_preferences()

@api_view(('GET',))
def preferences_stats(request):
    preference = Preferences()
    data = preference.get_data_object()
    return Response(data)

def export_preferences(request):
    preference = Preferences()
    results = preference.get_dataframe()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=preferences_export.csv'

    results.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
    return response

def export_inline(request):
    inline = Inline()
    results = inline.get_dataframe()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=inline_export.csv'

    results.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
    return response


@api_view(('GET',))
def inline_stats(request):
    inline = Inline()
    data = inline.get_data_object()
    return Response(data)
