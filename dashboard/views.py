from django.shortcuts import render
import os
from common.retrievedata import JGWApi

# Create your views here.
def index(request):
    return render(request, 'dashboard.html')

def test_sentry(request):
    division_error = 1/0

def retrieve_preferences(request):
    api = JGWApi()
    api.get_preferences()
