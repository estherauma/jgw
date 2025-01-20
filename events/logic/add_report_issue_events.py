from django.db import transaction
from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.logger import KunfuPandaLogger
from common.utils.date_utils import todays_date
from events.models import ReportIssueSubmittedEvent
from common.helpers.model_helpers.preference import (
    get_or_add_age_to_db,
    get_or_add_language_to_db,
    get_or_add_gender_to_db,
    get_or_add_country_to_db,
    get_or_add_country_state_to_db,
    get_or_add_organisation_to_db,
    get_or_add_route_to_db,
)

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/report_issue_events.log")


def fetch_report_issue_events_from_api():
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    latest_report_issue = ReportIssueSubmittedEvent.objects.last()
    if latest_report_issue:
        start_date = latest_report_issue.created_at.strftime("%Y-%m-%d")

    appEvents = AppEvents()
    latest_report_issue_events = appEvents.bigquery_report_issue_submitted_events(
        start_date=start_date, end_date=end_date
    )
    return latest_report_issue_events


@transaction.atomic
def fetch_report_issue_events_from_api_to_db():
    report_issue_events = fetch_report_issue_events_from_api() or []
    for report_issue_event in report_issue_events:
        try:
            add_report_issue_event_to_db(report_issue_event)
        except Exception as e:
            kunfu_panda_logger.error(f"An error occurred during report issue event creation: {str(e)}")
            transaction.set_rollback(True)
            raise

    kunfu_panda_logger.info(f"Added {len(report_issue_events)} report issue events to the database")


def add_report_issue_event_to_db(event):
    event_date = event.get("event_date")
    event_name = event.get("event_name")

    age = get_or_add_age_to_db(event.get("age"))
    language = get_or_add_language_to_db(event.get("language"))
    gender = get_or_add_gender_to_db(event.get("gender"))
    destination_state = get_or_add_country_state_to_db(event.get("destinationState"))
    destination = get_or_add_country_to_db(event.get("destination"), source="destination")
    origin = get_or_add_country_to_db(event.get("origin"), source="origin")
    organisation = get_or_add_organisation_to_db(event.get("organisation"))
    route = get_or_add_route_to_db(event.get("route"))

    ReportIssueSubmittedEvent.objects.create(
        event_date=event_date,
        event_name=event_name,
        age=age,
        language=language,
        gender=gender,
        device_id=event.get("deviceId"),
        app_id=event.get("appId"),
        organisation_access_code=event.get("organisationAccessCode"),
        organisation_code=event.get("organisationCode"),
        organisation=organisation,
        locale=event.get("locale"),
        destination_state=destination_state,
        destination=destination,
        origin=origin,
        route=route,
    )
