from datetime import datetime
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, StreamingHttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.writer.excel import save_virtual_workbook
import io
import csv
import json
from openpyxl.styles import Alignment, Font, PatternFill
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, CC_INLINE_EXPORT_ORG_NAMES
from common.utils.preferences import get_date_13_months_ago
from common.utils.request import get_form_filter_params
from core.filters import generic_filter_form_parser
from core.forms import DateRangeForm
from core.logic.file_export import generate_and_export_excel
from events.repository.bigquery_homepage_events_repository import get_user_counts_by_geo_country
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
    get_messaging_question_by_sectors,
    get_messaging_question_per_destination_counts,
    get_messaging_question_per_organisation_counts,
    get_messaging_question_per_origin_counts,
    get_user_counts_by_destination,
    messaging_question_stats_for_export,
    messaging_questions_count,
)
from users.utils import get_user_organisations
import pandas as pd
from io import BytesIO
from question.filters import (
    _lead_response_filter_date_range,
    lead_inline_question_response_filtered_queryset,
)
from .models import (
    InlineQuestionStandard,
    InlineQuestionAndKeysMatch,
    InlineQuestion,
    InlineQuestionResponse,
)
from events.models import BigqueryHomepageEventData
from question.repository.messaging_questions_standard import message_data_sent_filtered_queryset
from question.models import MessageDataSent
from question.models import LeadInlineQuestionResponse


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
    messaging_question_by_sectors = get_messaging_question_by_sectors(**filters, current_user=request.user)

    user_counts_by_geo_country = get_user_counts_by_destination(**filters, current_user=request.user)

    context = {
        "total_messaging_questions": total_messaging_questions,
        "messaging_question_per_origin": messaging_question_per_origin,
        "messaging_question_per_destination": messaging_question_per_destination,
        "messaging_question_per_organisation": messaging_question_per_organisation,
        "each_messaging_question_response": json.dumps(each_messaging_question_response_data, cls=DjangoJSONEncoder),
        "messaging_question_by_age": messaging_question_by_age,
        "messaging_question_by_gender": messaging_question_by_gender,
        "user_counts_by_geo_country": user_counts_by_geo_country,
        "messaging_question_by_sectors": messaging_question_by_sectors,
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


# Organisations that require the special inline export rules:
# drop the "Question Key" column and keep only the most recent same-day response.

def _dedupe_inline_responses_same_day(inline_data):
    """
    Remove duplicate inline question responses that happened on the same day,
    keeping only the most recent response for each (device, question) per day.

    Recency is determined by ``updated_at`` and falls back to ``created_at``.
    """
    def response_recency(record):
        return record.get("updated_at") or record.get("created_at")

    deduped = {}
    for record in inline_data:
        created_at = record.get("created_at")
        if created_at and timezone.is_aware(created_at):
            response_day = timezone.localtime(created_at).date()
        elif created_at:
            response_day = created_at.date()
        else:
            response_day = None

        key = (record.get("device_id"), record.get("question_key"), response_day)

        existing = deduped.get(key)
        if existing is None:
            deduped[key] = record
            continue

        new_ts = response_recency(record)
        existing_ts = response_recency(existing)
        if existing_ts is None or (new_ts is not None and new_ts > existing_ts):
            deduped[key] = record

    return list(deduped.values())


def export_inline_question_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=InlineQuestionFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    inline_data = get_all_inline_question_responses_data(**filters, current_user=request.user)

    user_orgs = get_user_organisations(request.user)
    organisations = [getattr(org, "name") for org in user_orgs]

    apply_cc_rules = (
        not request.user.is_superuser
        and any(org_name in CC_INLINE_EXPORT_ORG_NAMES for org_name in organisations)
    )
    include_question_key = not apply_cc_rules

    if apply_cc_rules:
        inline_data = _dedupe_inline_responses_same_day(inline_data)

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
    ]
    if include_question_key:
        headers.append("Question Key")
    headers.extend(["Question", "Response"])

    for idx, header in enumerate(headers, start=1):
        ws.cell(row=4, column=idx, value=header)

    for idx, data in enumerate(inline_data, start=5):
        created_at = (
            timezone.localtime(data["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
            if data["created_at"]
            else None
        )
        updated_at = (
            timezone.localtime(data["updated_at"]).strftime("%Y-%m-%d %H:%M:%S")
            if data["updated_at"]
            else None
        )
        route_value = data["route"] if data["route"] else None
        language_value = data["language"] if data["language"] else None
        origin_value = data["origin"] if data["origin"] else None
        destination_value = data["destination"] if data["destination"] else None
        organisation_sector_value = data["organisation_sector"] if data["organisation_sector"] else None
        organisation_value = data["organisation"] if data["organisation"] else None

        row_values = [
            created_at,
            updated_at,
            data["device_id"],
            language_value,
            origin_value,
            destination_value,
            organisation_sector_value,
            organisation_value,
            route_value,
        ]
        if include_question_key:
            row_values.append(data["question_key"])
        row_values.extend([data["title_text"], data["response"]])

        for col_idx, value in enumerate(row_values, start=1):
            ws.cell(row=idx, column=col_idx, value=value)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=inline_question_data.xlsx"

    wb.save(response)

    return response


def export_message_sent_data(request):
    """
    Optimized export function that handles large datasets without memory issues.
    Uses streaming CSV export for better performance with large data.
    """
    form_filter_params = get_form_filter_params(request=request, form_class=MessagingQuestionFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date") or get_date_13_months_ago()
    end_date = filters.get("end_date") or datetime.now().date()

    use_streaming = request.GET.get('streaming', 'true').lower() == 'true'
    
    if use_streaming:
        return export_message_sent_data_streaming(filters, start_date, end_date, current_user=request.user)
    else:
        return export_message_sent_data_excel(filters, start_date, end_date, current_user=request.user)


def export_message_sent_data_streaming(filters, start_date, end_date, current_user=None):
    """
    Streaming CSV export for large datasets - memory efficient
    """
    def data_generator():
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
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(headers)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        
        queryset = message_data_sent_filtered_queryset(
            queryset=MessageDataSent.objects.select_related("language", "destination", "organisation", "message_content"), 
            current_user=current_user,
            **filters
        )
        
        
        chunk_size = 1000
        total_processed = 0
        
        for chunk_start in range(0, queryset.count(), chunk_size):
            chunk = queryset[chunk_start:chunk_start + chunk_size]
            
            for message in chunk:
                api_created_at = (
                    timezone.localtime(message.api_created_at).strftime("%Y-%m-%d %H:%M:%S")
                    if message.api_created_at
                    else ""
                )
                api_updated_at = (
                    timezone.localtime(message.api_updated_at).strftime("%Y-%m-%d %H:%M:%S")
                    if message.api_updated_at
                    else ""
                )
                message_date = (
                    timezone.localtime(message.message_date).strftime("%Y-%m-%d %H:%M:%S")
                    if message.message_date
                    else ""
                )
                
                row = [
                    api_created_at,
                    api_updated_at,
                    message.message_id or "",
                    message.device_id or "",
                    message.language.name if message.language else "",
                    message.destination.name if message.destination else "",
                    message.organisation.name if message.organisation else "",
                    message.message_title or "",
                    message.message_title_english or "",
                    message.message_content.message if message.message_content else "",
                    message_date,
                    str(message.message_delivered) if message.message_delivered is not None else "",
                    str(message.message_delivered_date) if message.message_delivered_date else "",
                    str(message.message_queued) if message.message_queued is not None else "",
                    str(message.message_notification_sent_to_fcm) if message.message_notification_sent_to_fcm is not None else "",
                ]
                
                writer.writerow(row)
                total_processed += 1
                
                if total_processed % 100 == 0:
                    yield output.getvalue()
                    output.seek(0)
                    output.truncate(0)
            
            if output.getvalue():
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
    
    response = StreamingHttpResponse(
        data_generator(),
        content_type='text/csv'
    )
    response['Content-Disposition'] = f'attachment; filename="message_sent_data_{start_date}_to_{end_date}.csv"'
    return response


def export_message_sent_data_excel(filters, start_date, end_date, current_user=None):
    """
    Excel export for smaller datasets - uses chunked processing
    """
    
    
    queryset = message_data_sent_filtered_queryset(
        queryset=MessageDataSent.objects.select_related("language", "destination", "organisation", "message_content"), 
        current_user=current_user,
        **filters
    )
    total_count = queryset.count()
    
    
    if total_count > 50000:
        return HttpResponse(
            f"Dataset too large ({total_count:,} records). Please use streaming export by adding ?streaming=true to the URL.",
            status=400
        )
    
    wb = Workbook()
    ws = wb.active
    
    
    heading = f"Message Sent Data Report for the Period Starting {start_date} to {end_date}"
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=15)
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)
    
    
    info_cell = ws.cell(row=3, column=1, value=f"Total Records: {total_count:,}")
    info_cell.font = Font(italic=True)
    
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
        ws.cell(row=5, column=idx, value=header)
        ws.cell(row=5, column=idx).font = Font(bold=True)
    
    chunk_size = 1000
    row_number = 6
    
    for chunk_start in range(0, total_count, chunk_size):
        chunk = queryset[chunk_start:chunk_start + chunk_size]
        
        for message in chunk:
            api_created_at = (
                timezone.localtime(message.api_created_at).strftime("%Y-%m-%d %H:%M:%S")
                if message.api_created_at
                else ""
            )
            api_updated_at = (
                timezone.localtime(message.api_updated_at).strftime("%Y-%m-%d %H:%M:%S")
                if message.api_updated_at
                else ""
            )
            message_date = (
                timezone.localtime(message.message_date).strftime("%Y-%m-%d %H:%M:%S")
                if message.message_date
                else ""
            )
            
            ws.cell(row=row_number, column=1, value=api_created_at)
            ws.cell(row=row_number, column=2, value=api_updated_at)
            ws.cell(row=row_number, column=3, value=message.message_id or "")
            ws.cell(row=row_number, column=4, value=message.device_id or "")
            ws.cell(row=row_number, column=5, value=message.language.name if message.language else "")
            ws.cell(row=row_number, column=6, value=message.destination.name if message.destination else "")
            ws.cell(row=row_number, column=7, value=message.organisation.name if message.organisation else "")
            ws.cell(row=row_number, column=8, value=message.message_title or "")
            ws.cell(row=row_number, column=9, value=message.message_title_english or "")
            ws.cell(row=row_number, column=10, value=message.message_content.message if message.message_content else "")
            ws.cell(row=row_number, column=11, value=message_date)
            ws.cell(row=row_number, column=12, value=str(message.message_delivered) if message.message_delivered is not None else "")
            ws.cell(row=row_number, column=13, value=str(message.message_delivered_date) if message.message_delivered_date else "")
            ws.cell(row=row_number, column=14, value=str(message.message_queued) if message.message_queued is not None else "")
            ws.cell(row=row_number, column=15, value=str(message.message_notification_sent_to_fcm) if message.message_notification_sent_to_fcm is not None else "")
            
            row_number += 1
    
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f"attachment; filename=message_sent_data_{start_date}_to_{end_date}.xlsx"
    wb.save(response)
    return response


def generate_payment_questions_excel(filters=None):
    question_keys = [
        'swsPayForTravelAndVisa',
        'recruiterAskedForPayments',
        'swsAskedToMakeOtherPayments',
        'labourProviderAskedToMakePayment',
        'fishingFees',
        'swvAskedToPayFees',
        'didARecruitmentAgentAskYouToPayIllegitimateFees',
        'asvRecruiterAskedForPayments',
        'swsAskedToMakeOtherPayments',
        'labourProviderAskedToMakePayment',
    ]

    base_query = InlineQuestionResponse.objects.filter(
        inline_question__question__text__in=question_keys,
        response__translated_text__icontains='yes'
    )

    if filters:
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        if start_date:
            base_query = base_query.filter(
                inline_question__inline_question_standard__api_created_at__gte=start_date
            )
        if end_date:
            base_query = base_query.filter(
                inline_question__inline_question_standard__api_created_at__lte=end_date
            )
        
        organisations = filters.get('organisations')
        if organisations:
            base_query = base_query.filter(
                inline_question__inline_question_standard__org_info__name__in=organisations
            )
        
        destinations = filters.get('destination_countries')
        if destinations:
            base_query = base_query.filter(
                inline_question__inline_question_standard__destination__name__in=destinations
            )

    responses = base_query.select_related(
        'inline_question',
        'inline_question__inline_question_standard',
        'inline_question__question',
        'response',
        'inline_question__inline_question_standard__language',
        'inline_question__inline_question_standard__origin',
        'inline_question__inline_question_standard__destination',
        'inline_question__inline_question_standard__org_info',
        'inline_question__inline_question_standard__immigration_status',
        'inline_question__inline_question_standard__factory_farm',
    )

    question_text_to_key = dict(
        InlineQuestionAndKeysMatch.objects.filter(
            inline_question_key__in=question_keys
        ).values_list('inline_question', 'inline_question_key')
    )
    export_data = []
    for resp in responses:
        question_standard = resp.inline_question.inline_question_standard
        question_text = resp.inline_question.question.title_text
        question_key = question_text_to_key.get(question_text, '')
        
        geo_data = BigqueryHomepageEventData.objects.filter(
            device_id=question_standard.device_id
        ).first()
        
        api_created_at = question_standard.api_created_at.replace(tzinfo=None) if question_standard.api_created_at else None
        api_updated_at = question_standard.api_updated_at.replace(tzinfo=None) if question_standard.api_updated_at else None
        
        export_data.append({
            'Data Source ID': question_standard.data_source_id,
            'Device ID': question_standard.device_id,
            'App ID': question_standard.app_id,
            'Question Key': question_key,
            'Question Text': question_text,
            'Response': resp.response.translated_text if resp.response else 'N/A',
            'Locale': question_standard.locale,
            'Language': question_standard.language.name if question_standard.language else 'N/A',
            'Origin Country': question_standard.origin.name if question_standard.origin else 'N/A',
            'Destination Country': question_standard.destination.name if question_standard.destination else 'N/A',
            'Organisation': question_standard.org_info.name if question_standard.org_info else 'N/A',
            'Organisation Code': question_standard.org_code,
            'Organisation Work Code': question_standard.org_work_code,
            'Immigration Status': question_standard.immigration_status.name if question_standard.immigration_status else 'N/A',
            'Geo Country': geo_data.geo_country.name if geo_data and geo_data.geo_country else 'N/A',
            'Geo City': geo_data.geo_city if geo_data and geo_data.geo_city else 'N/A',
            'API Created At': api_created_at,
            'API Updated At': api_updated_at,
           
        })
    if export_data:
        df = pd.DataFrame(export_data)
        output = BytesIO()
        
        wb = Workbook()
        ws = wb.active
        ws.title = 'Payment Questions Responses'
        
        header_rows = []
        header_rows.append("Payment Inline Questions Export (Yes Responses)")
        
        if filters:
            filter_info = []
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            organisations = filters.get('organisation')
            destinations = filters.get('destination')
            
            if start_date or end_date:
                date_range = f"Date Range: {start_date or 'Start'} to {end_date or 'End'}"
                filter_info.append(date_range)
            
            if organisations:
                org_list = ', '.join(organisations) if isinstance(organisations, list) else str(organisations)
                filter_info.append(f"Organisations: {org_list}")
            
            if destinations:
                dest_list = ', '.join(destinations) if isinstance(destinations, list) else str(destinations)
                filter_info.append(f"Destinations: {dest_list}")
            
            if filter_info:
                header_rows.append("Applied Filters:")
                header_rows.extend([f"  • {info}" for info in filter_info])
            else:
                header_rows.append("No specific filters applied")
        else:
            header_rows.append("No filters applied - All data exported")
        
        for i, header_text in enumerate(header_rows, 1):
            ws.cell(row=i, column=1, value=header_text)
            if i == 1:  
                ws.cell(row=i, column=1).font = Font(bold=True, size=14)
            elif i == 2:  
                ws.cell(row=i, column=1).font = Font(bold=True, size=12)
        
        blank_row = len(header_rows) + 1
        
        headers = [
            'Data Source ID', 'Device ID', 'App ID','Question Key', 'Question Text', 'Response', 'Locale', 'Language', 'Origin Country',
            'Destination Country', 'Organisation', 'Organisation Code', 'Organisation Work Code',
            'Immigration Status', 'Geo Country', 'Geo City', 'API Created At',
            'API Updated At'
        ]
        for idx, header in enumerate(headers, 1):
            ws.cell(row=blank_row, column=idx, value=header)
            ws.cell(row=blank_row, column=idx).font = Font(bold=True)
        
        for row_idx, data_row in enumerate(df.values, blank_row + 1):
            for col_idx, value in enumerate(data_row, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        wb.save(output)
        output.seek(0)
        return output
    else:
        empty_df = pd.DataFrame(columns=[
            'Data Source ID', 'Device ID', 'App ID','Question Key', 'Question Text', 'Response', 'Locale', 'Language', 'Origin Country',
            'Destination Country', 'Organisation', 'Organisation Code', 'Organisation Work Code',
            'Immigration Status', 'Geo Country', 'Geo City', 'API Created At',
            'API Updated At'
        ])
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            empty_df.to_excel(writer, sheet_name='Payment Questions Responses', index=False)
        output.seek(0)
        return output


def export_payment_inline_questions(request):
    form_filter_params = get_form_filter_params(request=request, form_class=InlineQuestionFilterForm)
    filters = form_filter_params["filters"]
    
    excel_file = generate_payment_questions_excel(filters=filters)
    response = HttpResponse(
        excel_file,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=payment_inline_questions.xlsx"
    return response


def export_lead_questions_with_followups(request):
    """
    Exports lead questions with their follow-up and follow-up-to-follow-up questions to Excel
    in a hierarchical and easy-to-read format.
    """
    form_filter_params = get_form_filter_params(request=request, form_class=InlineQuestionFilterForm)
    filters = form_filter_params["filters"]
    start_date, end_date = _lead_response_filter_date_range(
        request.user,
        filters.get("start_date"),
        filters.get("end_date"),
    )

    wb = Workbook()
    ws = wb.active

    heading = f"Lead Questions with Follow-up Chain Report from {start_date} to {end_date}"

    lead_headers = [
        "Lead Question Details",
        "Created At",
        "Updated At",
        "Device ID",
        "Language",
        "Destination",
        "Organisation",
        "Organisation Code",
        "Immigration Status",
        "Factory Farm",
        "Page ID",
        "Page Title",
        "Question Key",
        "Question Text",
        "Value Key",
        "Value Option",
    ]

    ws.append([None] * 16)
    ws.append([heading] + [None] * 15)
    ws.append([None] * 16)
    ws.append(lead_headers)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=16)
    heading_cell = ws.cell(row=2, column=1)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)
    for idx in range(1, 17):
        ws.cell(row=4, column=idx).font = Font(bold=True)

    base_queryset = LeadInlineQuestionResponse.objects.select_related(
        'language',
        'destination',
        'organisation',
        'immigration_status',
        'factory_farm',
        'inline_question',
        'inline_question__question_category',
        'inline_question_response'
    ).prefetch_related(
        'followup_responses__inline_question',
        'followup_responses__inline_question__question_category',
        'followup_responses__inline_question_response',
        'followup_responses__followup_followup_responses__inline_question',
        'followup_responses__followup_followup_responses__inline_question__question_category',
        'followup_responses__followup_followup_responses__inline_question_response'
    )

    lead_questions = lead_inline_question_response_filtered_queryset(
        current_user=request.user,
        queryset=base_queryset,
        **filters,
    )

    def _dt(val):
        if not val:
            return None
        return timezone.localtime(val).strftime("%Y-%m-%d %H:%M:%S") if timezone.is_aware(val) else val.strftime("%Y-%m-%d %H:%M:%S")

    blank_row = [None] * 16

    for lead in lead_questions:
        ws.append(
            [
                "Lead Question",
                _dt(lead.created_at),
                _dt(lead.updated_at),
                lead.device_id,
                lead.language.name if lead.language else None,
                lead.destination.name if lead.destination else None,
                lead.organisation.name if lead.organisation else None,
                lead.organisation_code,
                lead.immigration_status.name if lead.immigration_status else None,
                lead.factory_farm.name if lead.factory_farm else None,
                lead.inline_question.page_id if lead.inline_question else None,
                lead.inline_question.page_title if lead.inline_question else None,
                lead.inline_question.question_key if lead.inline_question else None,
                lead.inline_question.question_text if lead.inline_question else None,
                lead.inline_question_response.response_key if lead.inline_question_response else None,
                lead.inline_question_response.response_text if lead.inline_question_response else None,
            ]
        )

        followups = lead.followup_responses.all()
        if followups:
            for followup in followups:
                ws.append(
                    [
                        "Follow-up Question",
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        followup.inline_question.question_key if followup.inline_question else None,
                        followup.inline_question.question_text if followup.inline_question else None,
                        followup.inline_question_response.response_key if followup.inline_question_response else None,
                        followup.inline_question_response.response_text if followup.inline_question_response else None,
                    ]
                )

                followup_followups = followup.followup_followup_responses.all()
                if followup_followups:
                    for ff in followup_followups:
                        ws.append(
                            [
                                "Follow-up-to-Follow-up Question",
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                ff.inline_question.question_key if ff.inline_question else None,
                                ff.inline_question.question_text if ff.inline_question else None,
                                ff.inline_question_response.response_key if ff.inline_question_response else None,
                                ff.inline_question_response.response_text if ff.inline_question_response else None,
                            ]
                        )

                ws.append(blank_row)

        ws.append(blank_row)

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 18
    ws.column_dimensions["F"].width = 18
    ws.column_dimensions["G"].width = 22
    ws.column_dimensions["H"].width = 18
    ws.column_dimensions["I"].width = 22
    ws.column_dimensions["J"].width = 18
    ws.column_dimensions["K"].width = 14
    ws.column_dimensions["L"].width = 26
    ws.column_dimensions["M"].width = 22
    ws.column_dimensions["N"].width = 60
    ws.column_dimensions["O"].width = 22
    ws.column_dimensions["P"].width = 60

    ws.freeze_panes = 'A5'

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=lead_questions_with_followups.xlsx"

    wb.save(response)
    return response
