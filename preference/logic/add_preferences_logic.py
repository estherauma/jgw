
from django.db import transaction

from common.const.value_const import NOT_SPECIFIED
from common.services.api_client import JustGoodWorkAPIClient
from common.utils.preferences import get_origin_and_destination_from_route
from preference.models import FactoryFarm, Organisation, OrganisationSector, Preference, SectorOfWork


def get_or_create_model_instance(model, value):
    if not value:
        instance, _ = model.objects.get_or_create(name=NOT_SPECIFIED)
    else:
        instance, _ = model.objects.get_or_create(name=value)
    return instance

def fetch_preferences_from_api(client, start_date='2019-01-01', end_date='2023-06-27'):
    return client.get_data(f"/preferences?startDate={start_date}&endDate={end_date}")


@transaction.atomic
def fetch_preferences_from_api_to_db():
    
    jgw_api_client = JustGoodWorkAPIClient()
    preferences = fetch_preferences_from_api(jgw_api_client)
    
    print("preferences: ", preferences)
    for preference in preferences:
        try:
            add_preference_to_db(preference)
        except Exception as e:
            print('An error occurred during preference creation:', str(e))
            transaction.set_rollback(True)
            raise


def add_preference_to_db(preference):
        organisation_sector = preference.get("organisationSector")
        organisation = preference.get("organisation")
        factory_farm = preference.get("factoryFarm")
        sectors_of_work = preference.get("sectorsOfWork")
        
        # add organisation_sector to db
        org_sector = add_organisation_sector_to_db(organisation_sector)
        
        # add organisation to db
        org = add_organisation_to_db(organisation)
        
        # add factory_farm to db
        fact_farm = add_factory_farm_to_db(factory_farm)
        
        # add preference to db
        route = preference.get('route') or NOT_SPECIFIED
        new_preference = Preference.objects.create(
            data_source_id= preference.get('_id'),
            device_id= preference.get('deviceId'),
            updated_at= preference.get('updatedAt'),
            location_of_potential_work= preference.get('location_of_potential_work'),
            gender= preference.get('gender'),
            age= preference.get('age'),
            route= route,
            locale= preference.get('locale'),
            app_id= preference.get('appId'),
            created_at= preference.get('createdAt'),
            language= preference.get('language'),
            organisation_sector=org_sector,
            factory_farm=fact_farm,
            organisation=org,
            origin= get_origin_and_destination_from_route(route).get('origin'),
            destination= get_origin_and_destination_from_route(route).get('destination'),
        )

        # Create SectorOfWork instances and associate them with the preference
        sec_of_work_list = add_sector_of_work_to_db(sectors_of_work)
        for sec_of_work in sec_of_work_list:
            new_preference.sectors_of_work.add(sec_of_work)

        return preference


def add_organisation_sector_to_db(organisation_sector: str) -> OrganisationSector:
    return get_or_create_model_instance(OrganisationSector, organisation_sector)

def add_organisation_to_db(organisation: str) -> Organisation:
    return get_or_create_model_instance(Organisation, organisation)

def add_factory_farm_to_db(factory_farm: str) -> FactoryFarm:
    return get_or_create_model_instance(FactoryFarm, factory_farm)

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
    