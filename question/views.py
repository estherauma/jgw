import csv
from django.http import HttpResponse
from django.shortcuts import render
from openpyxl import Workbook
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


def export_question_stats(request, question_type):
    
    export_name = f"{question_type}_question_stats"
    work_sheets_data = [
        {
            'name': 'Sheet1',
            'headers': ['Column1', 'Column2', 'Column3'],
            'contents': [
                ['Value11', 'Value12', 'Value13'],
                ['Value21', 'Value22', 'Value23'],
            ],
        },
        {
            'name': 'Sheet2',
            'headers': ['AnotherColumn1', 'AnotherColumn2', 'AnotherColumn3'],
            'contents': [
                ['ValueA1', 'ValueA2', 'ValueA3'],
                ['ValueB1', 'ValueB2', 'ValueB3'],
            ],
        },
    ]
    
    workbook = Workbook()
    
    for work_sheet_data in work_sheets_data:
        # Extract sheet data
        name = work_sheet_data['name']
        headers = work_sheet_data['headers']
        contents = work_sheet_data['contents']

        # Create a new sheet with the given name
        sheet = workbook.create_sheet(title=name)

        # Write headers to the sheet
        sheet.append(headers)

        # Write contents to the sheet
        for content_row in contents:
            sheet.append(content_row)
    
    # Make the first sheet active
    workbook.active = 1
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={export_name}.xlsx'
    
    workbook.save(response)
        
    return response
    