from django.db import transaction
from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.helpers.preference_helpers.country import get_lat_lon
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
        
        for location in location_events:
            city = location.get("city")
            country = location.get("country")
            region = location.get("region")
            user_count = location.get("user_count", 0)
            
            # Get latitude and longitude using OpenStreetMap (Nominatim)
            latitude, longitude = get_lat_lon(city, country)
            
            if latitude and longitude:
                UserLocation.objects.update_or_create(
                    city=city,
                    country=country,
                    region=region,
                    defaults={
                        "latitude": latitude,
                        "longitude": longitude,
                        "user_count": user_count
                    }
                )
        
        kunfu_panda_logger.info(f"{len(location_events)} location events saved to the database.")
        
    except Exception as e:
        kunfu_panda_logger.error(f"An error occurred while saving location events: {str(e)}")
        raise 