from django.http import HttpResponse
from django.shortcuts import render
from core.filters import generic_filter_form_parser
from core.forms import GenericFilterForm
from core.logic.file_export import generate_and_export_excel
from preference.repository.preference import get_all_organisations
from question.repository.messaging_questions_standard import (
    get_messaging_question_per_destination_counts, 
    get_messaging_question_per_origin_counts,
    messaging_questions_count
)



def messaging_question(request):
    
    if request.method == 'GET':
        filter_form = GenericFilterForm()
        total_messaging_questions = messaging_questions_count()
        messaging_question_per_origin = get_messaging_question_per_origin_counts()
        messaging_question_per_destination = get_messaging_question_per_destination_counts()
        
    else:
        filter_form = GenericFilterForm(request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)
            
        total_messaging_questions = messaging_questions_count(**filters)
        messaging_question_per_origin = get_messaging_question_per_origin_counts(**filters)
        messaging_question_per_destination = get_messaging_question_per_destination_counts(**filters)
    

    context = {
        "total_messaging_questions": total_messaging_questions,
        "messaging_question_per_origin": messaging_question_per_origin,
        "messaging_question_per_destination": messaging_question_per_destination,
        'filter_form': filter_form,
    }
    return render(
        request,
        "question/messaging_question.html", 
        context = context
    )


def question_stats_for_export(filters):
    messaging_question_per_origin = get_messaging_question_per_origin_counts(**filters)
    messaging_question_per_destination = get_messaging_question_per_destination_counts(**filters)
    return {
        "messaging_question_per_origin": messaging_question_per_origin,
        "messaging_question_per_destination": messaging_question_per_destination,
    }

def export_question_stats(request):
    if request.method == 'POST':
        filter_form = GenericFilterForm(request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get('organisation', None)
        
        if organisations is None:
            organisations = get_all_organisations()
        
        export_dict = {}
        for organisation in organisations:
            export_dict[organisation.name] = question_stats_for_export({**filters, 'organisations': [organisation]})
            
        return generate_and_export_excel(export_dict)