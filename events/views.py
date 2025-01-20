from openpyxl.styles import Alignment, Font
from django.http import HttpResponse
from django.shortcuts import render
from openpyxl import Workbook
from common.utils.request import get_form_filter_params
from core.forms import DateRangeForm
from core.logic.file_export import generate_and_export_excel
from events.forms import EventsDataFilterForm
from events.models import LinksClickEvent, TelephoneClickEvent, ReportIssueSubmittedEvent
from events.repository.bigquery_chapters_feedback_repository import get_chapters_feedback
from events.repository.chapters_opened_repository import get_chapters_opened_data
from datetime import datetime
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE


def what_matters_to_workers(request):
    form_filter_params = get_form_filter_params(request=request, form_class=EventsDataFilterForm)
    filters = form_filter_params["filters"]

    filter_form = form_filter_params["filter_form"]

    date_range_form = DateRangeForm()

    chapters_feedback = get_chapters_feedback(**filters, current_user=request.user)
    chapters_opened_data = get_chapters_opened_data(**filters, current_user=request.user)

    context = {
        "chapters_opened_data": chapters_opened_data,
        "chapters_feedback": chapters_feedback,
        "filter_form": filter_form,
        "date_range_form": date_range_form,
    }
    return render(request, "events/what-matters-to-workers.html", context=context)


def export_what_matters_to_workers_stats(request):
    if request.method == "POST":
        form_filter_params = get_form_filter_params(request=request, form_class=EventsDataFilterForm)
        filters = form_filter_params["filters"]

        chapters_feedback = get_chapters_feedback(current_user=request.user, **filters)
        smiles_count = [cf.get("smiles") for cf in chapters_feedback]
        frowns_counts = [cf.get("frowns") for cf in chapters_feedback]
        feedback_labels = [cf.get("chapter_text") for cf in chapters_feedback]

        chapters_opened_data = get_chapters_opened_data(current_user=request.user, **filters)

        if chapters_opened_data:
            export_dict = {
                "chapters": {
                    "what_matters_to_workers_all": {
                        "labels": chapters_opened_data["labels"],
                        "counts": chapters_opened_data["chapteropened_all"],
                    },
                    "what_matters_to_workers_unique": {
                        "labels": chapters_opened_data["labels"],
                        "counts": chapters_opened_data["chapteropened_unique"],
                    },
                    "user_feedback_smiles": {"labels": feedback_labels, "counts": smiles_count},
                    "user_feedback_frowns": {"labels": feedback_labels, "counts": frowns_counts},
                }
            }
            return generate_and_export_excel(export_dict, filename="what_matters_to_workers_stats")


def export_link_clicks_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=EventsDataFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date") or APPLICATION_POSSIBLE_START_DATE
    end_date = filters.get("end_date") or datetime.now().date()

    link_clicks = LinksClickEvent.objects.filter(event_date__range=(start_date, end_date)).values(
        "event_date", "event_name", "link"
    )

    wb = Workbook()
    ws = wb.active

    heading = f"Link Clicks Report for the Period Starting {start_date} to {end_date}"
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=3)

    headers = ["Event Date", "Event Name", "Link"]
    for col, header in enumerate(headers, start=1):
        ws.cell(row=3, column=col, value=header)

    for row, click in enumerate(link_clicks, start=4):
        ws.cell(row=row, column=1, value=click["event_date"].strftime("%Y-%m-%d"))
        ws.cell(row=row, column=2, value=click["event_name"])
        ws.cell(row=row, column=3, value=click["link"])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=link_clicks_data.xlsx"

    wb.save(response)

    return response


def export_telephone_clicks_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=EventsDataFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date") or APPLICATION_POSSIBLE_START_DATE
    end_date = filters.get("end_date") or datetime.now().date()

    telephone_clicks = TelephoneClickEvent.objects.filter(event_date__range=(start_date, end_date)).values(
        "event_date", "event_name", "link"
    )

    wb = Workbook()
    ws = wb.active

    heading = f"Telephone Clicks Report for the Period Starting {start_date} to {end_date}"
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=3)

    headers = ["Event Date", "Event Name", "Link"]
    for col, header in enumerate(headers, start=1):
        ws.cell(row=3, column=col, value=header)

    for row, click in enumerate(telephone_clicks, start=4):
        ws.cell(row=row, column=1, value=click["event_date"].strftime("%Y-%m-%d"))
        ws.cell(row=row, column=2, value=click["event_name"])
        ws.cell(row=row, column=3, value=click["link"])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=telephone_clicks_data.xlsx"

    wb.save(response)

    return response


def export_report_issue_data(request):
    form_filter_params = get_form_filter_params(request=request, form_class=EventsDataFilterForm)
    filters = form_filter_params["filters"]
    start_date = filters.get("start_date") or APPLICATION_POSSIBLE_START_DATE
    end_date = filters.get("end_date") or datetime.now().date()

    report_issues = ReportIssueSubmittedEvent.objects.filter(event_date__range=(start_date, end_date)).values(
        "event_date",
        "event_name",
        "device_id",
        "app_id",
        "organisation__name",
        "destination__name",
        "origin__name",
        "destination_state__name",
        "language__name",
        "age__range",
        "gender__name",
        "locale",
        "route__name",
    )

    wb = Workbook()
    ws = wb.active

    heading = f"Report Issue Submitted Data for the Period Starting {start_date} to {end_date}"
    heading_cell = ws.cell(row=2, column=1, value=heading)
    heading_cell.alignment = Alignment(horizontal="center", vertical="center")
    heading_cell.font = Font(bold=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=13)

    headers = [
        "Event Date",
        "Event Name",
        "Device ID",
        "App ID",
        "Organisation",
        "Destination",
        "Origin",
        "Destination State",
        "Language",
        "Age",
        "Gender",
        "Locale",
        "Route",
    ]

    for col, header in enumerate(headers, start=1):
        ws.cell(row=3, column=col, value=header)

    for row, issue in enumerate(report_issues, start=4):
        ws.cell(row=row, column=1, value=issue["event_date"].strftime("%Y-%m-%d %H:%M:%S"))
        ws.cell(row=row, column=2, value=issue["event_name"])
        ws.cell(row=row, column=3, value=issue["device_id"])
        ws.cell(row=row, column=4, value=issue["app_id"])
        ws.cell(row=row, column=5, value=issue["organisation__name"])
        ws.cell(row=row, column=6, value=issue["destination__name"])
        ws.cell(row=row, column=7, value=issue["origin__name"])
        ws.cell(row=row, column=8, value=issue["destination_state__name"])
        ws.cell(row=row, column=9, value=issue["language__name"])
        ws.cell(row=row, column=10, value=issue["age__range"])
        ws.cell(row=row, column=11, value=issue["gender__name"])
        ws.cell(row=row, column=12, value=issue["locale"])
        ws.cell(row=row, column=13, value=issue["route__name"])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=report_issue_data.xlsx"

    wb.save(response)
    return response
