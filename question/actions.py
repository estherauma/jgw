from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponse
import openpyxl


def export_unique_questions(self, request, queryset):
    """Exports questions unique by the route and question text"""

    # unique_by_route_and_question_text_qs = queryset.order_by(
    #     "question__text", "inline_question_standard__preference__route__name"
    # ).distinct("question__text", "question__text")
    # ~Q(question__text__isnull=True)
    unique_by_route_and_question_text_qs = queryset.filter()

    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = "attachment; file_name='exported_data.xlsx'"

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Exported Data"
    worksheet.append(["Question", "Route"])

    for obj in unique_by_route_and_question_text_qs:
        route = (
            obj.inline_question_standard.preference.route.name
            if obj.inline_question_standard.preference
            else obj.inline_question_standard.preference
        )
        worksheet.append([obj.question.text, route])

    workbook.save(response)
    return response
