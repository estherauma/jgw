from django.shortcuts import render
from core.filters import generic_filter_form_parser
from core.logic.file_export import generate_and_export_excel
from preference.repository.preference_repository import get_all_organisations_list
from question.forms import (
    InlineQuestionFilterForm, 
    InlineQuestionOnlyFilterForm, 
    MessagingQuestionFilterForm
)
from question.repository.inline_questions_standard import (
    each_inline_question_response, 
    get_inline_question_per_destination_counts, 
    get_inline_question_per_language_counts, 
    get_inline_question_per_organisation_counts, 
    get_inline_question_per_origin_counts, 
    inline_questions_count
)
from question.repository.messaging_questions_standard import (
    get_messaging_question_per_destination_counts, 
    get_messaging_question_per_origin_counts,
    inline_question_response,
    messaging_questions_count,
    question_stats_for_export
)



def messaging_question(request):
    
    if request.method == 'GET':
        filter_form = MessagingQuestionFilterForm(request=request)
        total_messaging_questions = messaging_questions_count(current_user = request.user)
        messaging_question_per_origin = get_messaging_question_per_origin_counts(current_user = request.user)
        messaging_question_per_destination = get_messaging_question_per_destination_counts(current_user = request.user)
        
    else:
        filter_form = MessagingQuestionFilterForm(request=request, data=request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)
            
        total_messaging_questions = messaging_questions_count(
            **filters,
            current_user = request.user
        )
        messaging_question_per_origin = get_messaging_question_per_origin_counts(
            **filters,
            current_user = request.user
        )
        messaging_question_per_destination = get_messaging_question_per_destination_counts(
            **filters,
            current_user = request.user
        )
    

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



def export_messaging_question_stats(request):
    if request.method == 'POST':
        filter_form = MessagingQuestionFilterForm(request=request, data=request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get('organisation', None)
        
        if organisations is None:
            # otherwise , get all loggedin user's organisations
            organisations = get_all_organisations_list()
        
        export_dict = {}
        for organisation in organisations:
            export_dict[organisation] = question_stats_for_export({
                **filters, 
                'organisations': [organisation],
                'current_user': request.user
            })
            
        return generate_and_export_excel(export_dict, filename="messaging_question_stats")
    
    
def inline_question(request):
    
    if request.method == 'GET':
        filter_form = InlineQuestionFilterForm(request=request)
        total_inline_questions = inline_questions_count(current_user = request.user)
        inline_question_per_origin = get_inline_question_per_origin_counts(current_user = request.user)
        inline_question_per_destination = get_inline_question_per_destination_counts(current_user = request.user)
        inline_question_per_organisation = get_inline_question_per_organisation_counts(current_user = request.user)
        inline_question_per_language = get_inline_question_per_language_counts(current_user = request.user)
        inline_question_response_data = inline_question_response()
        
    else:
        filter_form = InlineQuestionFilterForm(request=request, data=request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)
            
        total_inline_questions = inline_questions_count(
            **filters,
            current_user = request.user
        )
        inline_question_per_origin = get_inline_question_per_origin_counts(
            **filters,
            current_user = request.user
        )
        inline_question_per_destination = get_inline_question_per_destination_counts(
            **filters,
            current_user = request.user
        )
        inline_question_per_organisation = get_inline_question_per_organisation_counts(
            **filters,
            current_user = request.user
        )
        inline_question_per_language = get_inline_question_per_language_counts(
            **filters,
            current_user = request.user
        )
        inline_question_response_data = inline_question_response()
    

    context = {
        "total_inline_questions": total_inline_questions,
        "inline_question_per_origin": inline_question_per_origin,
        "inline_question_per_destination": inline_question_per_destination,
        "inline_question_per_organisation": inline_question_per_organisation,
        "inline_question_per_language": inline_question_per_language,
        "inline_question_response_data": inline_question_response_data,
        'filter_form': filter_form,
        "each_inline_question_response": each_inline_question_response(),
        "inline_question_only_form": InlineQuestionOnlyFilterForm(),
    }
    return render(
        request,
        "question/inline_question.html", 
        context = context
    )
    
    
def export_inline_question_stats(request):
    if request.method == 'POST':
        filter_form = InlineQuestionFilterForm(request=request, data=request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get('organisation', None)
        
        if organisations is None:
            # TODO: otherwise , get all loggedin user's organisations
            organisations = get_all_organisations_list()
        
        export_dict = {
            # TODO: add all organisations stats to the export_dict
        }
        for organisation in organisations:
            export_dict[organisation] = question_stats_for_export({
                **filters, 
                'organisations': [organisation],
                "current_user": request.user
            })
        return generate_and_export_excel(export_dict, filename="inline_question_stats")