from django.http import response
from django.shortcuts import render
import os

from pandas.core import api
from common.retrievedata import JGWApi
from common.preferences import Preferences
from rest_framework.response import Response
from rest_framework.decorators import api_view


preference = Preferences()
# Create your views here.
def index(request):
    return render(request, 'dashboard.html')

def test_sentry(request):
    division_error = 1/0

def retrieve_preferences(request):
    api = JGWApi()
    api.get_preferences()

@api_view(('GET',))
def preferences_stats(request):
    data = preference.get_data_object()
    return Response(data)

