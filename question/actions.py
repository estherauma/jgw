from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponse
import openpyxl


def export_unique_questions(self, request, queryset):
    """Exports questions unique by the route and question text"""
    
    unique_by_route_and_question_text_qs = queryset.select_related(
        'question', 
        'inline_question_standard'
    ).values('inline_question_standard__preference__route__name', 'question__text').distinct()

    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = "attachment; filename=question-responses-data.xlsx"

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Exported Data"
    worksheet.append(["Question", "Route"])
    
    for obj in unique_by_route_and_question_text_qs:
        question_text = obj.get("question__text")
        route = obj.get("inline_question_standard__preference__route__name")
        worksheet.append([question_text, route])

    # Adjust column widths based on content length
    for column_cells in worksheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2  # Adding extra space

    workbook.save(response)
    return response
