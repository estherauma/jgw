from django.http import HttpResponse
from django.shortcuts import render
from core.filters import generic_filter_form_parser
from core.forms import GenericFilterForm
from core.logic.file_export import generate_and_export_excel
from preference.repository.preference import get_all_organisations
from question.repository.inline_questions_standard import get_inline_question_per_destination_counts, get_inline_question_per_language_counts, get_inline_question_per_organisation_counts, get_inline_question_per_origin_counts, inline_questions_count
from question.repository.messaging_questions_standard import (
    get_messaging_question_per_destination_counts, 
    get_messaging_question_per_origin_counts,
    messaging_questions_count,
    question_stats_for_export
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



def export_question_stats(request):
    if request.method == 'POST':
        filter_form = GenericFilterForm(request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get('organisation', None)
        
        if organisations is None:
            # otherwise , get all loggedin user's organisations
            organisations = get_all_organisations()
        
        export_dict = {}
        for organisation in organisations:
            export_dict[organisation.name] = question_stats_for_export({**filters, 'organisations': [organisation]})
            
        return generate_and_export_excel(export_dict)
    
    
def inline_question(request):
    
    if request.method == 'GET':
        filter_form = GenericFilterForm()
        total_inline_questions = inline_questions_count()
        inline_question_per_origin = get_inline_question_per_origin_counts()
        inline_question_per_destination = get_inline_question_per_destination_counts()
        inline_question_per_organisation = get_inline_question_per_organisation_counts()
        inline_question_per_language = get_inline_question_per_language_counts()
        
    else:
        filter_form = GenericFilterForm(request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)
        else:
            # filters = {}
            print(filter_form.errors)
            
        total_inline_questions = inline_questions_count(**filters)
        inline_question_per_origin = get_inline_question_per_origin_counts(**filters)
        inline_question_per_destination = get_inline_question_per_destination_counts(**filters)
        inline_question_per_organisation = get_inline_question_per_organisation_counts(**filters)
        inline_question_per_language = get_inline_question_per_language_counts(**filters)
    

    context = {
        "total_inline_questions": total_inline_questions,
        "inline_question_per_origin": inline_question_per_origin,
        "inline_question_per_destination": inline_question_per_destination,
        "inline_question_per_organisation": inline_question_per_organisation,
        "inline_question_per_language": inline_question_per_language,
        'filter_form': filter_form,
    }
    return render(
        request,
        "question/inline_question.html", 
        context = context
    )