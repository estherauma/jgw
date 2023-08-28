from django.shortcuts import render

from events.repository.bigquery_chapters_data import get_firstopen_homepage_data, get_user_per_chapters

# Create your views here.
def what_matters_to_workers(request):
    get_user_per_chapters()
    get_firstopen_homepage_data()
    return render(request, "events/what-matters-to-workers.html")