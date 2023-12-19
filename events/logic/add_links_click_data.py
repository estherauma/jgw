from django.db import transaction

from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.logger import KunfuPandaLogger
from common.utils.date_utils import todays_date
from events.models import LinksClickEvent


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/links_click_events.log")


def fetch_links_click_events_from_api():
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    # get the last time links click events were fetched
    latest_links_click_event = LinksClickEvent.objects.last()
    if latest_links_click_event:
        start_date = latest_links_click_event.created_at.strftime("%Y-%m-%d")

    appEvents = AppEvents()
    latest_links_click_events_result = appEvents.bigquery_links_click_event(
        start_date=start_date, end_date=end_date
    )
    return latest_links_click_events_result


@transaction.atomic
def fetch_links_click_events_from_api_to_db():
    links_click_events = fetch_links_click_events_from_api() or []
    for links_click_event in links_click_events:
        try:
            links_click_events_to_db(links_click_event)
        except Exception as e:
            KunfuPandaLogger.error(f"An error occurred during links clicl events creation: {str(e)}")
            transaction.set_rollback(True)
            raise

    kunfu_panda_logger.info(f"Added {len(links_click_events)} links click events to the database")


def links_click_events_to_db(links_click_event):
    event_name = links_click_event.get("event_name")
    event_date = links_click_event.get("event_date")
    link = links_click_event.get("link")

    LinksClickEvent.objects.create(event_date=event_date, event_name=event_name, link=link)
