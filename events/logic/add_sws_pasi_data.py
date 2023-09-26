
from django.db import transaction

from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.helpers.model_helpers.preference import get_or_add_age_to_db, get_or_add_country_to_db, get_or_add_gender_to_db, get_or_add_language_to_db, get_or_add_organisation_to_db
from common.logger import KunfuPandaLogger
from common.utils.date_utils import date_to_datetime, todays_date
from common.utils.strings import camel_case_to_space_separated
from events.models import SwsPasiEvent
from preference.models import Organisation
from preference.tasks import translate_and_clean_preferences_fields

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/sws_pasi_events.log")

def fetch_sws_pasi_events_from_api():
    start_date= APPLICATION_POSSIBLE_START_DATE
    end_date= todays_date()
    
    # get the last time sws pasi events were fetched
    latest_sws_pasi_event = SwsPasiEvent.objects.last()
    if latest_sws_pasi_event:
        start_date = latest_sws_pasi_event.created_at.strftime("%Y-%m-%d")
        
    appEvents = AppEvents()
    latest_sws_pasi_events_result = appEvents.bigquery_SWS_PASI_events(
        start_date=start_date,
        end_date=end_date
    )
    return latest_sws_pasi_events_result


@transaction.atomic
def fetch_sws_pasi_events_from_api_to_db():
    
    sws_pasi_events = fetch_sws_pasi_events_from_api() or []
    
    for sws_pasi_event in sws_pasi_events:
        try:
            add_sws_pasi_events_to_db(sws_pasi_event)
        except Exception as e:
            KunfuPandaLogger.error(f'An error occurred during sws pasi events creation: {str(e)}')
            transaction.set_rollback(True)
            raise
        
    kunfu_panda_logger.info(f'Added {len(sws_pasi_events)} sws pasi events to the database')
    
    # call celery to the translate, gender, language and sector of work functions
    translate_and_clean_preferences_fields()

def format_org_name(org_name: str):
    if "place" in org_name:
        return "placeuk"
    else:
        return org_name

def add_sws_pasi_events_to_db(sws_pasi_event):
    timestamp = sws_pasi_event.get('event_timestamp')
    user_pseudo_id = sws_pasi_event.get('user_pseudo_id')
    event_bundle_sequence_id = sws_pasi_event.get('event_bundle_sequence_id')
    
    constructed_event_id = f"{timestamp}-{user_pseudo_id}-{event_bundle_sequence_id}"
    if SwsPasiEvent.objects.filter(constructed_event_id=constructed_event_id).exists():
        return
        
    event_name = sws_pasi_event.get("event_name")
    event_date = sws_pasi_event.get("event_date")
        
    age = sws_pasi_event.get("age")
    language = sws_pasi_event.get("language")
    gender = sws_pasi_event.get("gender")
    organisation = sws_pasi_event.get("organisation")
    destination = sws_pasi_event.get("destination")
    
    device_id = sws_pasi_event.get("deviceId")
    app_id = sws_pasi_event.get("appId")
    
    language_data = get_or_add_language_to_db(language)
    destination_data = get_or_add_country_to_db(destination, source="destination")
    age_data = get_or_add_age_to_db(age)
    gender_data = get_or_add_gender_to_db(gender)
    
    #org name from event name
    splitted_event_name_list = event_name.split("_")
    org_name = splitted_event_name_list[len(splitted_event_name_list) - 1]
    org = Organisation.objects.filter(name__contains=format_org_name(
        camel_case_to_space_separated(org_name)
    )).first()
    
    SwsPasiEvent.objects.create(
        constructed_event_id = constructed_event_id,
        event_name = event_name,
        event_created_at = date_to_datetime(event_date),
        age = age_data,
        language = language_data,
        gender = gender_data,
        device_id = device_id,
        app_id = app_id,
        organisation = org,
        destination = destination_data,
    )