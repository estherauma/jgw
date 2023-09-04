from django.shortcuts import render

from events.repository.bigquery_chapters_data import get_chapters_users, get_chapters_counts

# Create your views here.
def what_matters_to_workers(request):
    chapters_counts = get_chapters_counts()
    chapters_users = get_chapters_users()
    print(chapters_counts)
    return render(request, "events/what-matters-to-workers.html")