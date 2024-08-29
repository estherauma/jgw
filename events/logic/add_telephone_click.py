from django.db import transaction

from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.logger import KunfuPandaLogger
from common.utils.date_utils import todays_date
from events.models import TelephoneClickEvent


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/links_click_events.log")

def fetch_telephone_click_events_from_api():
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    latest_telephone_click_event = TelephoneClickEvent.objects.last()
    if latest_telephone_click_event:
        start_date = latest_telephone_click_event.created_at.strftime("%Y-%m-%d")

    appEvents = AppEvents()
    latest_telephone_click_events_result = appEvents.bigquery_telephone_click_event(
        start_date=start_date, end_date=end_date
    )
    return latest_telephone_click_events_result


@transaction.atomic
def fetch_telephone_click_events_from_api_to_db():
    telephone_click_events = fetch_telephone_click_events_from_api() or []
    for telephone_click_event in telephone_click_events:
        try:
            telephone_click_events_to_db(telephone_click_event)
        except Exception as e:
            KunfuPandaLogger.error(f"An error occurred during telephone click events creation: {str(e)}")
            transaction.set_rollback(True)
            raise

    kunfu_panda_logger.info(f"Added {len(telephone_click_events)} telephone click events to the database")


def telephone_click_events_to_db(telephone_click_event):
    event_name = telephone_click_event.get("event_name")
    event_date = telephone_click_event.get("event_date")
    link = telephone_click_event.get("link")

    TelephoneClickEvent.objects.create(event_date=event_date, event_name=event_name, link=link)
