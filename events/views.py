from django.shortcuts import render

from events.repository.bigquery_chapters_data import get_chapters_users, get_chapters_counts
from events.repository.bigquery_chapters_opened import get_chapters_opened

# Create your views here.
def what_matters_to_workers(request):
    chapters_opened = get_chapters_opened()
    
    context ={
        "chapters_opened": chapters_opened
    }
    return render(request, "events/what-matters-to-workers.html", context=context)