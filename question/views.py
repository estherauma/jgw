from datetime import datetime
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.utils.preferences import get_date_13_months_ago
from common.utils.request import get_form_filter_params
from core.filters import generic_filter_form_parser
from core.forms import DateRangeForm
from core.logic.file_export import generate_and_export_excel
from question.forms import InlineQuestionFilterForm, MessagingQuestionFilterForm
from question.repository.inline_questions_standard import (
    each_inline_question_response,
    get_all_inline_question_responses_data,
    get_inline_question_per_destination_counts,
    get_inline_question_per_language_counts,
    get_inline_question_per_organisation_counts,
    get_inline_question_per_origin_counts,
    inline_question_response,
    inline_question_responses_count,
    inline_question_stats_for_export,
    inline_questions_count,
)
from question.repository.messaging_questions_standard import (
    each_messaging_question_response,
    get_all_message_data_sent,
    get_all_messaging_question_responses_data,
    get_messaging_question_by_age,
    get_messaging_question_by_gender,
    get_messaging_question_per_destination_counts,
    get_messaging_question_per_organisation_counts,
    get_messaging_question_per_origin_counts,
    messaging_question_stats_for_export,
    messaging_questions_count,
)
from users.utils import get_user_organisations


def messaging_question(request):
    form_filter_params = get_form_filter_params(request=request, form_class=MessagingQuestionFilterForm)
    filters = form_filter_params["filters"]
    filter_form = form_filter_params["filter_form"]

    date_range_form = DateRangeForm()

    total_messaging_questions = messaging_questions_count(**filters, current_user=request.user)
    messaging_question_per_origin = get_messaging_question_per_origin_counts(
        **filters, current_user=request.user
    )
    messaging_question_by_age = get_messaging_question_by_age(**filters, current_user=request.user)
    messaging_question_by_gender = get_messaging_question_by_gender(**filters, current_user=request.user)
    messaging_question_per_destination = get_messaging_question_per_destination_counts(
        **filters, current_user=request.user
    )
    messaging_question_per_organisation = get_messaging_question_per_organisation_counts(
        **filters, current_user=request.user
    )
    each_messaging_question_response_data = each_messaging_question_response(
        **filters, current_user=request.user
    )

    context = {
        "total_messaging_questions": total_messaging_questions,
        "messaging_question_per_origin": messaging_question_per_origin,
        "messaging_question_per_destination": messaging_question_per_destination,
        "messaging_question_per_organisation": messaging_question_per_organisation,
        "each_messaging_question_response": each_messaging_question_response_data,
        "messaging_question_by_age": messaging_question_by_age,
        "messaging_question_by_gender": messaging_question_by_gender,
        "filter_form": filter_form,
        "date_range_form": date_range_form,
    }
    return render(request, "question/messaging_question.html", context=context)


def export_messaging_question_stats(request):
    if request.method == "POST":
        filter_form = MessagingQuestionFilterForm(request=request, data=request.POST)

        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get("organisation", None)

        if organisations is None:
            user_orgs = get_user_organisations(request.user)
            organisations = [getattr(org, "name") for org in user_orgs]

        export_dict = {
            "all": messaging_question_stats_for_export(
                {**filters, "organisations": organisations, "current_user": request.user}
            )
        }
        for organisation in organisations:
            export_dict[organisation] = messaging_question_stats_for_export(
                {**filters, "organisations": [organisation], "current_user": request.user}
            )

        return generate_and_export_excel(export_dict, filename="messaging_question_stats")


def inline_question(request):
    form_filter_params = get_form_filter_params(request=request, form_class=InlineQuestionFilterForm)
    filters = form_filter_params["filters"]
    filter_form = form_filter_params["filter_form"]

    date_range_form = DateRangeForm()

    total_inline_questions = inline_questions_count(**filters, current_user=request.user)
    inline_question_per_origin = get_inline_question_per_origin_counts(**filters, current_user=request.user)
    inline_question_per_destination = get_inline_question_per_destination_counts(
        **filters, current_user=request.user
    )
    inline_question_per_organisation = get_inline_question_per_organisation_counts(
        **filters, current_user=request.user
    )
    inline_question_per_language = get_inline_question_per_language_counts(
        **filters, current_user=request.user
    )
    inline_question_response_data = inline_question_response()

    total_inline_question_responses = inline_question_responses_count(**filters, current_user=request.user)
    each_inline_question_response_data = each_inline_question_response(**filters, current_user=request.user)

    context = {
        "total_inline_questions": total_inline_questions,
        "total_inline_question_responses": total_inline_question_responses,
        "inline_question_per_origin": inline_question_per_origin,
        "inline_question_per_destination": inline_question_per_destination,
        "inline_question_per_organisation": inline_question_per_organisation,
        "inline_question_per_language": inline_question_per_language,
        "inline_question_response_data": inline_question_response_data,
        "filter_form": filter_form,
        "date_range_form": date_range_form,
        "each_inline_question_response": each_inline_question_response_data,
    }
    return render(request, "question/inline_question.html", context=context)


def export_inline_question_stats(request):
    if request.method == "POST":
        filter_form = InlineQuestionFilterForm(request=request, data=request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get("organisation", None)

        if organisations is None:
            user_orgs = get_user_organisations(request.user)
            organisations = [getattr(org, "name") for org in user_orgs]

        export_dict = {
            "all": inline_question_stats_for_export(
                {**filters, "organisations": organisations, "current_user": request.user}
            )
        }

        for organisation in organisations:
            export_dict[organisation] = inline_question_stats_for_export(
                {**filters, "organisations": [organisation], "current_user": request.user}
            )
        return generate_and_export_excel(export_dict, filename="inline_question_stats")


def export_messaging_question_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=MessagingQuestionFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    messaging_data = get_all_messaging_question_responses_data(**filters, current_user=request.user)

    wb = Workbook()
    ws = wb.active

    heading = f"Messaging Question Report for the Period Starting {start_date} to {end_date}"
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=15)
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)

    headers = [
        "API Created At",
        "API Updated At",
        "Data Source ID",
        "Device ID",
        "App ID",
        "Message ID",
        "Locale",
        "Original Language",
        "Origin",
        "Destination",
        "Organisation Sector",
        "Factory Farm",
        "Organisation",
        "Question",
        "Response",
        "Translated Response",
    ]

    for idx, header in enumerate(headers, start=1):
        ws.cell(row=4, column=idx, value=header)

    for idx, data in enumerate(messaging_data, start=5):
        api_created_at = timezone.localtime(data["api_created_at"]).strftime("%Y-%m-%d %H:%M:%S")
        api_updated_at = timezone.localtime(data["api_updated_at"]).strftime("%Y-%m-%d %H:%M:%S")

        ws.cell(row=idx, column=1, value=api_created_at)
        ws.cell(row=idx, column=2, value=api_updated_at)
        ws.cell(row=idx, column=3, value=data["data_source_id"])
        ws.cell(row=idx, column=4, value=data["device_id"])
        ws.cell(row=idx, column=5, value=data["app_id"])
        ws.cell(row=idx, column=6, value=data["message_id"])
        ws.cell(row=idx, column=7, value=data["locale"])
        ws.cell(row=idx, column=8, value=data["language"])
        ws.cell(row=idx, column=9, value=data["origin"])
        ws.cell(row=idx, column=10, value=data["destination"])
        ws.cell(row=idx, column=11, value=data["organisation_sector"])
        ws.cell(row=idx, column=12, value=data["factory_farm"])
        ws.cell(row=idx, column=13, value=data["organisation"])
        ws.cell(row=idx, column=14, value=data["question"])
        ws.cell(row=idx, column=15, value=data["response"])
        ws.cell(row=idx, column=16, value=data["translated_response"])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=messaging_question_data.xlsx"

    wb.save(response)

    return response


def export_inline_question_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=InlineQuestionFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    inline_data = get_all_inline_question_responses_data(**filters, current_user=request.user)

    wb = Workbook()
    ws = wb.active

    heading = f"Inline Question Report for All Routes from the Period Starting {start_date} to {end_date}"
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)

    headers = [
        "Created At",
        "Updated At",
        "Device ID",
        "Original Language",
        "Origin",
        "Destination",
        "Organisation Sector",
        "Organisation",
        "Route",
        "Question Key",
        "Question",
        "Response",
    ]

    for idx, header in enumerate(headers, start=1):
        ws.cell(row=4, column=idx, value=header)

    for idx, data in enumerate(inline_data, start=5):
        created_at = data["created_at"]
        updated_at = data["updated_at"]
        route_value = data["route"] if data["route"] else None
        language_value = data["language"] if data["language"] else None
        origin_value = data["origin"] if data["origin"] else None
        destination_value = data["destination"] if data["destination"] else None
        organisation_sector_value = data["organisation_sector"] if data["organisation_sector"] else None
        organisation_value = data["organisation"] if data["organisation"] else None

        ws.cell(row=idx, column=1, value=created_at)
        ws.cell(row=idx, column=2, value=updated_at)
        ws.cell(row=idx, column=3, value=data["device_id"])
        ws.cell(row=idx, column=4, value=language_value)
        ws.cell(row=idx, column=5, value=origin_value)
        ws.cell(row=idx, column=6, value=destination_value)
        ws.cell(row=idx, column=7, value=organisation_sector_value)
        ws.cell(row=idx, column=8, value=organisation_value)
        ws.cell(row=idx, column=9, value=route_value)
        ws.cell(row=idx, column=10, value=data["question_key"])
        ws.cell(row=idx, column=11, value=data["title_text"])
        ws.cell(row=idx, column=12, value=data["response"])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=inline_question_data.xlsx"

    wb.save(response)

    return response


def export_message_sent_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=MessagingQuestionFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date") or get_date_13_months_ago()
    end_date = filters.get("end_date") or datetime.now().date()

    message_data = get_all_message_data_sent(**filters, current_user=request.user)

    wb = Workbook()
    ws = wb.active

    heading = f"Message Sent Data Report for the Period Starting {start_date} to {end_date}"
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=15)
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)

    headers = [
        "API Created At",
        "API Updated At",
        "Message ID",
        "Device ID",
        "Language",
        "Destination",
        "Organisation",
        "Message Title",
        "Message Title English",
        "Actual Message Content",
        "Message Date",
        "Message Delivered",
        "Message Delivered Date",
        "Message Queued",
        "Notification Sent to FCM",
    ]

    for idx, header in enumerate(headers, start=1):
        ws.cell(row=4, column=idx, value=header)

    for idx, data in enumerate(message_data, start=5):
        api_created_at = (
            timezone.localtime(data.get("api_created_at")).strftime("%Y-%m-%d %H:%M:%S")
            if data.get("api_created_at")
            else ""
        )
        api_updated_at = (
            timezone.localtime(data.get("api_updated_at")).strftime("%Y-%m-%d %H:%M:%S")
            if data.get("api_updated_at")
            else ""
        )

        message_date = (
            timezone.localtime(data.get("message_date")).strftime("%Y-%m-%d %H:%M:%S")
            if data.get("message_date")
            else ""
        )

        ws.cell(row=idx, column=1, value=api_created_at)
        ws.cell(row=idx, column=2, value=api_updated_at)
        ws.cell(row=idx, column=3, value=data.get("message_id", ""))
        ws.cell(row=idx, column=4, value=data.get("device_id", ""))
        ws.cell(row=idx, column=5, value=data.get("language", ""))
        ws.cell(row=idx, column=6, value=data.get("destination", ""))
        ws.cell(row=idx, column=7, value=data.get("organisation", ""))
        ws.cell(row=idx, column=8, value=data.get("message_title", ""))
        ws.cell(row=idx, column=9, value=data.get("message_title_english", ""))
        ws.cell(row=idx, column=10, value=data.get("actual_message", ""))
        ws.cell(row=idx, column=11, value=message_date)
        ws.cell(row=idx, column=12, value=str(data.get("message_delivered", "")))
        ws.cell(row=idx, column=13, value=str(data.get("message_delivered_date", "")))
        ws.cell(row=idx, column=14, value=str(data.get("message_queued", "")))
        ws.cell(row=idx, column=15, value=str(data.get("message_notification_sent_to_FCM", "")))

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=message_sent_data.xlsx"
    wb.save(response)
    return response
