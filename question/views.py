from django.shortcuts import render
from core.filters import generic_filter_form_parser
from core.forms import GenericFilterForm
from question.models import MessagingQuestionStandard
from question.repository.messaging_questions_standard import (
    get_messaging_question_per_destination_counts, 
    get_messaging_question_per_origin_counts,
    messaging_questions_count
)



def messaging_question(request):
    
    if request.method != 'POST':
        filter_form = GenericFilterForm()
        total_messaging_questions = messaging_questions_count()
        messaging_question_per_origin = get_messaging_question_per_origin_counts()
        messaging_question_per_destination = get_messaging_question_per_destination_counts()
        
    else:
        filter_form = GenericFilterForm(request.POST)
        if filter_form.is_valid():
            (start_date, end_date, origins, destinations) = generic_filter_form_parser(filter_form)
            print(start_date, end_date, origins, destinations)
            
        total_messaging_questions = messaging_questions_count(
            start_date = start_date,
            end_date = end_date,
            destination_countries = destinations,
            origin_countries = origins,
        )
        
        messaging_question_per_origin = get_messaging_question_per_origin_counts(
            start_date = start_date,
            end_date = end_date,
            destination_countries = destinations,
            origin_countries = origins,
        )
        
        messaging_question_per_destination = get_messaging_question_per_destination_counts(
            start_date = start_date,
            end_date = end_date,
            destination_countries = destinations,
            origin_countries = origins,
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
