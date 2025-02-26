from django.db import transaction
from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.helpers.model_helpers.preference import get_or_add_country_to_db
from common.utils.date_utils import todays_date
from events.models import UserLocation
from common.logger import KunfuPandaLogger

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/user_engagement_location.log")

def fetch_user_engagement_location_from_bigquery():
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()
    latest_location = UserLocation.objects.last()
    if latest_location:
        start_date = latest_location.created_at.strftime("%Y-%m-%d")
        
    appEvents = AppEvents()
    latest_location_result = appEvents.fetch_location_data(
        start_date=start_date,
        end_date=end_date
    )
    return latest_location_result

# @transaction.atomic
def fetch_and_save_user_engagement_location_to_db():
    try:
        location_events = fetch_user_engagement_location_from_bigquery()
        print("location_events", len(location_events))
        for location in location_events:
            event_date = location.get("event_date")
            user_pseudo_id = location.get("user_pseudo_id")
            country = location.get("country")
            country = get_or_add_country_to_db(country)

            UserLocation.objects.create(
                event_date=event_date,
                user_pseudo_id=user_pseudo_id,
                country=country,
            )
        
        kunfu_panda_logger.info(f"{len(location_events)} location events saved to the database.")
        
    except Exception as e:
        kunfu_panda_logger.error(f"An error occurred while saving location events: {str(e)}")
        raise 