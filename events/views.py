from django.shortcuts import render
from core.logic.file_export import generate_and_export_excel
from events.repository.bigquery_chapters_feedback_repository import get_chapters_feedback

from events.repository.chapters_opened_repository import get_chapters_opened


# Create your views here.
def what_matters_to_workers(request):
    chapters_opened = get_chapters_opened()
    chapters_feedback = get_chapters_feedback()

    context = {"chapters_opened": chapters_opened, "chapters_feedback": chapters_feedback}
    return render(request, "events/what-matters-to-workers.html", context=context)


def export_what_matters_to_workers_stats(request):
    if request.method == "POST":
        chapters_feedback = get_chapters_feedback()

        smiles_count = [cf.get("smiles") for cf in chapters_feedback]
        frowns_counts = [cf.get("frowns") for cf in chapters_feedback]
        labels = [cf.get("number_key") for cf in chapters_feedback]

        export_dict = {
            "chapters": {
                "what_matters_to_workers": get_chapters_opened(),
                "user_feedback_smiles": {"labels": labels, "counts": smiles_count},
                "user_feedback_frowns": {"labels": labels, "counts": frowns_counts},
            },
        }
        return generate_and_export_excel(export_dict, filename="what_matters_to_workers_stats")
