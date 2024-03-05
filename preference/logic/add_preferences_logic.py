from django.db import transaction

from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.helpers.model_helpers.preference import (
    add_sector_of_work_to_db,
    get_or_add_age_to_db,
    get_or_add_country_state_to_db,
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
    get_or_add_gender_to_db,
    get_or_add_language_to_db,
    get_or_add_location_of_potential_work_to_db,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
    get_or_add_route_to_db,
)
from common.logger import KunfuPandaLogger
from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date
from common.helpers.preference_helpers.country import (
    get_data_destination,
    get_data_origin,
)
from common.utils.helpers import can_use_cached_data
from preference.models import Preference
from preference.tasks import translate_and_clean_preferences_fields
from scripts.load_dev_data import PreferenceDataCache


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/preference_tasks.log")


def fetch_preferences_from_api(client):
    if can_use_cached_data():
        return PreferenceDataCache().get_data()

    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

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
            kunfu_panda_logger.error(f"An error occurred during preference creation: {str(e)}")
            transaction.set_rollback(True)
            raise

    kunfu_panda_logger.info(f"Added {len(preferences)} preferences to the database")

    # call celery to the translate, gender, language and sector of work functions
    translate_and_clean_preferences_fields()


def add_preference_to_db(preference):
    # check if already exists
    if Preference.objects.filter(data_source_id=preference.get("_id")).exists():
        return

    organisation_sector = preference.get("organisationSector")
    organisation = preference.get("organisation")
    factory_farm = preference.get("factoryFarm")
    sectors_of_work = preference.get("sectorsOfWork")
    sectors = preference.get("sectors")
    location_of_potential_work = preference.get("location_of_potential_work")
    gender = preference.get("gender")
    age = preference.get("age")
    language = preference.get("language")
    route = preference.get("route") or NOT_SPECIFIED

    origin = get_data_origin(route=route, api_origin=preference.get("locale"))
    destination = get_data_destination(
        route=route,
        api_destination=preference.get("destination"),
        location_of_potential_work=location_of_potential_work,
    )

    destination_state = preference.get("destinationState")

    # related fields
    organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)
    organisation_data = get_or_add_organisation_to_db(organisation)
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)
    location_of_potential_work_data = get_or_add_location_of_potential_work_to_db(location_of_potential_work)

    gender_data = get_or_add_gender_to_db(gender)
    age_data = get_or_add_age_to_db(age)
    language_data = get_or_add_language_to_db(language)
    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    api_destination_data = get_or_add_country_to_db(preference.get("destination"), source="destination")
    destination_state_data = get_or_add_country_state_to_db(destination_state)
    route_data = get_or_add_route_to_db(route)

    new_preference = Preference.objects.create(
        data_source_id=preference.get("_id"),
        device_id=preference.get("deviceId"),
        locale=preference.get("locale"),
        app_id=preference.get("appId"),
        api_created_at=preference.get("createdAt"),
        api_updated_at=preference.get("updatedAt"),
        location_of_potential_work=location_of_potential_work_data,
        gender=gender_data,
        age=age_data,
        language=language_data,
        origin=origin_data,
        destination=destination_data,
        destination_state=destination_state_data,
        route=route_data,
        organisation_sector=organisation_sector_data,
        factory_farm=factory_farm_data,
        organisation=organisation_data,
        api_destination=api_destination_data,
    )

    # Create SectorsOfWork instances and associate them with the preference
    final_sectors_of_work = sectors if sectors else sectors_of_work
    sec_of_work_list = add_sector_of_work_to_db(final_sectors_of_work)
    for sec_of_work in sec_of_work_list:
        new_preference.sectors_of_work.add(sec_of_work)
