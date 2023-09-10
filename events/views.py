from django.shortcuts import render
from events.repository.bigquery_chapters_feedback_repository import get_chapters_feedback

from events.repository.chapters_opened_repository import get_chapters_opened

# Create your views here.
def what_matters_to_workers(request):
    chapters_opened = get_chapters_opened()
    chapters_feedback = get_chapters_feedback()
    
    context ={
        "chapters_opened": chapters_opened,
        "chapters_feedback": chapters_feedback
    }
    return render(request, "events/what-matters-to-workers.html", context=context)