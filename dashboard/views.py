from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'dashboard.html')

def test_sentry(request):
    division_error = 1/0
