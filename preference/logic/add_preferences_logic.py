
from common.services.api_client import JustGoodWorkAPIClient
from preference.models import NOT_SPECIFIED, FactoryFarm, Organisation, OrganisationSector, SectorOfWork

preferences = [{'_id': '6486133489f5f2ecb2582151',
  'deviceId': 'jgw-vanilla-157b84322970cbf4-KAZ -> GBR',
  'updatedAt': '2023-06-22T11:16:15.914Z',
  'location_of_potential_work': 'GBR',
  'gender': 'женский',
  'age': '31-40',
  'factoryFarm': '',
  'organisationSector': 'agriculture',
  'organisation': 'Seasonal Worker Scheme - Generic',
  'route': 'KAZ -> GBR',
  'locale': 'KAZ',
  'appId': 'jgw-vanilla',
  '__v': 0,
  'createdAt': '2023-06-11T18:32:20.189Z',
  'sectorsOfWork': ['agriculture'],
  'language': 'ru-gc'},
               {'_id': '6486133489f5f2ecb2582151',
  'deviceId': 'jgw-vanilla-157b84322970cbf4-KAZ -> GBR',
  'updatedAt': '2023-06-22T11:16:15.914Z',
  'location_of_potential_work': 'GBR',
  'gender': 'женский',
  'age': '31-40',
  'factoryFarm': '',
  'organisationSector': 'agriculture',
  'organisation': 'Seasonal Worker Scheme - Upper Tier',
  'route': 'KAZ -> GBR',
  'locale': 'KAZ',
  'appId': 'jgw-vanilla',
  '__v': 0,
  'createdAt': '2023-06-11T18:32:20.189Z',
  'sectorsOfWork': ['agriculture', 'construction'],
  'language': 'ru-gc'}
               ]


def get_or_create_model_instance(model, value):
    if not value:
        instance, _ = model.objects.get_or_create(name=NOT_SPECIFIED)
    else:
        instance, _ = model.objects.get_or_create(name=value)
    return instance

def fetch_preferences_from_api(client):
    return client.get_data("/preferences")


def fetch_preferences_from_api_to_db():
    # jgw_api_client = JustGoodWorkAPIClient()
    # preferences = fetch_preferences_from_api(jgw_api_client)

    for preference in preferences:
        organisation_sector = preference.get("organisationSector")
        organisation = preference.get("organisation")
        factory_farm = preference.get("factoryFarm")
        sectors_of_work = preference.get("sectorsOfWork")
        
        # add organisation_sector to db
        org_sector = add_organisation_sector_to_db(organisation_sector)
        
        # add organisation to db
        org = add_organisation_to_db(organisation)
        
        # add factory_farm to db
        factory_farm = add_factory_farm_to_db(factory_farm)
        
        # add sectors_of_work to db
        sectors_of_work = add_sector_of_work_to_db(sectors_of_work)
        
        print("org: ", org)
        print("factory_farm: ", factory_farm)
        print("sectors_of_work: ", sectors_of_work)
        print("org_sector: ", org_sector)
        
        # add preference to db

def add_organisation_sector_to_db(organisation_sector):
    return get_or_create_model_instance(OrganisationSector, organisation_sector)

def add_organisation_to_db(organisation):
    return get_or_create_model_instance(Organisation, organisation)

def add_factory_farm_to_db(factory_farm):
    return get_or_create_model_instance(FactoryFarm, factory_farm)

def add_sector_of_work_to_db(sectors_of_work):
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
    