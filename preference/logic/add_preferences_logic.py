
from django.db import transaction

from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.custom_libs.pandas.pycountry import aplha_code_from_country_name, country_name_from_aplha_code
from common.helpers.model_helpers.get_create import get_or_create_model_instance
from common.logger import KunfuPandaLogger
from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date
from common.utils.preferences import get_origin_and_destination_from_route
from preference.models import (
    Age, Country, FactoryFarm, Gender, Organisation, OrganisationSector, Preference, SectorOfWork, Language, Route
    )



kunfu_panda_logger = KunfuPandaLogger()


def fetch_preferences_from_api(client):
    start_date= APPLICATION_POSSIBLE_START_DATE
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



def get_or_add_organisation_sector_to_db(organisation_sector: str) -> OrganisationSector:
    return get_or_create_model_instance(OrganisationSector, organisation_sector)

def get_or_add_organisation_to_db(organisation: str) -> Organisation:
    return get_or_create_model_instance(Organisation, organisation)

def get_or_add_factory_farm_to_db(factory_farm: str) -> FactoryFarm:
    return get_or_create_model_instance(FactoryFarm, factory_farm)

def get_or_add_country_to_db(country_name: str, source="generic") -> Country:
        if country_name:
            country_instance, _ = Country.objects.get_or_create(
                code= aplha_code_from_country_name(country_name) or NOT_SPECIFIED,
                name= country_name_from_aplha_code(country_name) or NOT_SPECIFIED
            )
            return country_instance
        else:
            country_instance, _ = Country.objects.get_or_create(
                code= NOT_SPECIFIED,
                name= NOT_SPECIFIED
            )
            return country_instance

def get_or_add_gender_to_db(gender: str) -> Gender:
    return get_or_create_model_instance(Gender, gender)

def get_or_add_age_to_db(age_range: str) -> Age:
    age_instance, _ = Age.objects.get_or_create(range= age_range or NOT_SPECIFIED)
    return age_instance


def get_or_add_language_to_db(language_name: str) -> Language:
    return get_or_create_model_instance(Language, language_name)

def get_or_add_route_to_db(route_name: str) -> Route:
    return get_or_create_model_instance(Route, route_name)

def add_sector_of_work_to_db(sectors_of_work: list[str]) -> list[SectorOfWork]:
    sector_list = []
    
    # Check if sectors_of_work is empty
    if not sectors_of_work:
        sector, _ = SectorOfWork.objects.get_or_create(name=NOT_SPECIFIED)
        sector_list.append(sector)
    else:
        for sector_name in sectors_of_work:
            sector, _ = SectorOfWork.objects.get_or_create(name=sector_name)
            sector_list.append(sector)

    return sector_list
    