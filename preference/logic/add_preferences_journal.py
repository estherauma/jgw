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
    get_or_add_organisation_access_code,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
    get_or_add_route_to_db,
    get_or_add_immigration_status_to_db
)
from common.logger import KunfuPandaLogger
from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date
from common.helpers.preference_helpers.country import (
    get_data_destination,
    get_data_origin,
)
from preference.logic.add_orgcode_to_preferences import add_organisation_data_to_db
from preference.logic.update_perference_organisation_info import update_preferences_journal_org_info_from_organisation, update_preferences_org_info_from_organisation
from preference.models import OrganisationData, PreferenceHistory

from preference.tasks import translate_and_clean_preferences_fields


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/preference_tasks.log")


def fetch_preferences_journal_from_api(client):
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    latest_preference = PreferenceHistory.objects.last()
    if latest_preference:
        start_date = latest_preference.created_at.strftime("%Y-%m-%d")

    return client.get_data(f"/preferences-history?startDate={start_date}&endDate={end_date}")


BATCH_SIZE = 5000


@transaction.atomic
def fetch_preferences_journal_from_api_to_db():
    add_organisation_data_to_db()
    jgw_api_client = JustGoodWorkAPIClient()
    preferences_history = fetch_preferences_journal_from_api(jgw_api_client) or []

    preferences_objects = [create_preference_journal_object(preference_history) for preference_history in preferences_history]
    PreferenceHistory.objects.bulk_create(preferences_objects, batch_size=BATCH_SIZE, ignore_conflicts=True)

    kunfu_panda_logger.info(f"Added {len(preferences_objects)} preferences journal to the database")

    translate_and_clean_preferences_fields()

    update_preferences_journal_org_info_from_organisation()


def create_preference_journal_object(preference_history):
    organisation_sector = preference_history.get("organisationSector")
    organisation = preference_history.get("organisation")
    org_info = preference_history.get("organisationCode")
    factory_farm = preference_history.get("factoryFarm")
    sectors_of_work = preference_history.get("sectorsOfWork")
    sector_of_work_list = preference_history.get("sectorOfWork")
    sectors = preference_history.get("sectors")
    location_of_potential_work = preference_history.get("location_of_potential_work")
    gender = preference_history.get("gender")
    age = preference_history.get("age")
    language = preference_history.get("language")
    route = preference_history.get("route") or NOT_SPECIFIED
    immigration_status = preference_history.get("immigrationStatus")

    origin = get_data_origin(route=route, api_origin=preference_history.get("locale") or preference_history.get("origin"))
    destination = get_data_destination(
        route=route,
        api_destination=preference_history.get("destination"),
        location_of_potential_work=location_of_potential_work,
    )

    destination_state = preference_history.get("destinationState")
    organisation_access_code = preference_history.get("organisationAccessCode")

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
    api_destination_data = get_or_add_country_to_db(preference_history.get("destination"), source="destination")
    destination_state_data = get_or_add_country_state_to_db(destination_state)
    route_data = get_or_add_route_to_db(route)
    organisation_access_code_data = get_or_add_organisation_access_code(organisation_access_code)

    immigration_status_instance = get_or_add_immigration_status_to_db(immigration_status)

    org_info_data = None
    if org_info:
        try:
            org_info_data = OrganisationData.objects.get(org_code=org_info)
        except OrganisationData.DoesNotExist:
            kunfu_panda_logger.warning(f"No OrganisationData found for org_code: {org_info}")

    new_preference_history = PreferenceHistory(
        data_source_id=preference_history.get("_id"),
        device_id=preference_history.get("deviceId"),
        locale=preference_history.get("locale"),
        app_id=preference_history.get("appId"),
        api_created_at=preference_history.get("createdAt"),
        api_updated_at=preference_history.get("updatedAt"),
        location_of_potential_work=location_of_potential_work_data,
        gender=gender_data,
        age=age_data,
        language=language_data,
        origin=origin_data,
        destination=destination_data,
        destination_state=destination_state_data,
        immigration_status=immigration_status_instance,
        route=route_data,
        org_code = org_info,
        organisation_sector=organisation_sector_data,
        factory_farm=factory_farm_data,
        organisation=organisation_data,
        api_destination=api_destination_data,
        organisation_access_code=organisation_access_code_data,
        org_info=org_info_data,
    )

    final_sectors_of_work = None
    if sector_of_work_list:
        final_sectors_of_work = sector_of_work_list

    if sectors_of_work:
        final_sectors_of_work = sectors_of_work

    if sectors:
        final_sectors_of_work = sectors

    sec_of_work_list = add_sector_of_work_to_db(final_sectors_of_work)
    new_preference_history.save()
    new_preference_history.sectors_of_work.set(sec_of_work_list)

    return new_preference_history