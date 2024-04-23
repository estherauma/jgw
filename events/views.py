from django.shortcuts import render
from common.utils.request import get_form_filter_params
from core.logic.file_export import generate_and_export_excel
from events.forms import EventsDataFilterForm
from events.repository.bigquery_chapters_feedback_repository import get_chapters_feedback

from events.repository.chapters_opened_repository import (
    get_chapters_opened,
    get_chapters_opened_unique_by_users,
)


# Create your views here.
def what_matters_to_workers(request):
    form_filter_params = get_form_filter_params(request=request, form_class=EventsDataFilterForm)
    filters = form_filter_params["filters"]
    filter_form = form_filter_params["filter_form"]

    chapters_opened = get_chapters_opened(**filters, current_user=request.user)
    chapters_opened_by_unique_user = get_chapters_opened_unique_by_users(**filters, current_user=request.user)
    chapters_feedback = get_chapters_feedback(**filters, current_user=request.user)

    context = {
        "chapters_opened": chapters_opened,
        "chapters_opened_by_unique_user": chapters_opened_by_unique_user,
        "chapters_feedback": chapters_feedback,
        "filter_form": filter_form,
    }
    return render(request, "events/what-matters-to-workers.html", context=context)


def export_what_matters_to_workers_stats(request):
    if request.method == "POST":
        form_filter_params = get_form_filter_params(request=request, form_class=EventsDataFilterForm)
        filters = form_filter_params["filters"]
        chapters_feedback = get_chapters_feedback(current_user=request.user,**filters)
        smiles_count = [cf.get("smiles") for cf in chapters_feedback]
        frowns_counts = [cf.get("frowns") for cf in chapters_feedback]
        labels = [cf.get("chapter_text") for cf in chapters_feedback]

        chapters_opened = get_chapters_opened(current_user=request.user, **filters)
        export_dict = {
            "chapters": {
                "what_matters_to_workers": chapters_opened,
                "user_feedback_smiles": {"labels": labels, "counts": smiles_count},
                "user_feedback_frowns": {"labels": labels, "counts": frowns_counts},
            },
        }
        return generate_and_export_excel(export_dict, filename="what_matters_to_workers_stats")
