
from django.db import transaction

from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.helpers.model_helpers.preference import (
    add_sector_of_work_to_db,
    get_or_add_age_to_db,
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
    get_or_add_gender_to_db,
    get_or_add_language_to_db,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
    get_or_add_route_to_db
)
from common.logger import KunfuPandaLogger
from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import previous_dates, todays_date
from common.utils.preferences import get_origin_and_destination_from_route
from preference.models import Preference
from preference.tasks import translate_preferences_fields



kunfu_panda_logger = KunfuPandaLogger(log_file="kunfu_panda_logs/preference_tasks.log")


def fetch_preferences_from_api(client):
    # start_date= APPLICATION_POSSIBLE_START_DATE
    start_date= previous_dates()
    end_date= todays_date()
    
    # get the last time preferences were fetched
    latest_preference = Preference.objects.last()
    if latest_preference:
        start_date = latest_preference.created_at.strftime("%Y-%m-%d")
        
    return client.get_data(f"/preferences?startDate={start_date}&endDate={end_date}")


@transaction.atomic
def fetch_preferences_from_api_to_db():
    
    jgw_api_client = JustGoodWorkAPIClient()
    preferences = fetch_preferences_from_api(jgw_api_client) or []
    
    for preference in preferences:
        try:
            add_preference_to_db(preference)
        except Exception as e:
            kunfu_panda_logger.error(f'An error occurred during preference creation: {str(e)}')
            transaction.set_rollback(True)
            raise
        
    kunfu_panda_logger.info(f'Added {len(preferences)} preferences to the database')
    
    # call celery to the translate, gender, language and sector of work functions
    translate_preferences_fields.delay()


def add_preference_to_db(preference):
        # check if already exists
        if Preference.objects.filter(data_source_id=preference.get("_id")).exists():
            return
            
        organisation_sector = preference.get("organisationSector")
        organisation = preference.get("organisation")
        factory_farm = preference.get("factoryFarm")
        sectors_of_work = preference.get("sectorsOfWork")
        location_of_potential_work = preference.get('location_of_potential_work')
        gender = preference.get('gender')
        age = preference.get('age')
        language= preference.get('language')
        route = preference.get('route') or NOT_SPECIFIED
        origin= get_origin_and_destination_from_route(route).get('origin')
        destination= get_origin_and_destination_from_route(route).get('destination')
        destination_state = preference.get('destinationState')
        
        # related fields 
        organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)
        organisation_data = get_or_add_organisation_to_db(organisation)
        factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)
        location_of_potential_work_data = get_or_add_country_to_db(location_of_potential_work, "location_of_potential_work_data")
        gender_data = get_or_add_gender_to_db(gender)
        age_data = get_or_add_age_to_db(age)
        language_data = get_or_add_language_to_db(language)
        origin_data = get_or_add_country_to_db(origin, "origin_data")
        destination_data = get_or_add_country_to_db(destination, "destination_data")
        destination_state_data = get_or_add_country_to_db(destination_state, "destination_state_data")
        route_data = get_or_add_route_to_db(route)
        
        new_preference = Preference.objects.create(
            data_source_id = preference.get("_id"),
            device_id = preference.get("deviceId"),
            locale = preference.get("locale"),
            app_id = preference.get("appId"),
            api_created_at = preference.get("createdAt"),
            api_updated_at = preference.get("updatedAt"),
            location_of_potential_work = location_of_potential_work_data,
            gender = gender_data,
            age = age_data,
            language = language_data,
            origin = origin_data,
            destination = destination_data,
            destination_state = destination_state_data,
            route = route_data,
            organisation_sector = organisation_sector_data,
            factory_farm = factory_farm_data,
            organisation = organisation_data ,      
        )

        # Create SectorsOfWork instances and associate them with the preference
        
        sec_of_work_list = add_sector_of_work_to_db(sectors_of_work)
        for sec_of_work in sec_of_work_list:
            new_preference.sectors_of_work.add(sec_of_work)


    