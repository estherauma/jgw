from common.const.value_const import NOT_SPECIFIED
from common.custom_libs.language_codes import get_language_name
from common.custom_libs.pycountry import aplha_code_from_country_name, country_name_from_aplha_code
from common.helpers.model_helpers.get_create import get_or_create_model_instance
from common.helpers.preference_helpers.country import normalize_country_name
from common.helpers.preference_helpers.organisation import normalize_organisation_name
from preference.models import Age, Country, FactoryFarm, Gender, Language, Organisation, OrganisationSector, Route, SectorOfWork


def get_or_add_organisation_sector_to_db(organisation_sector: str) -> OrganisationSector:
    return get_or_create_model_instance(OrganisationSector, organisation_sector)

def get_or_add_organisation_to_db(organisation_name: str) -> Organisation:
    normalized_organisation_name = normalize_organisation_name(organisation_name)
    return get_or_create_model_instance(Organisation, normalized_organisation_name)

def get_or_add_factory_farm_to_db(factory_farm: str) -> FactoryFarm:
    return get_or_create_model_instance(FactoryFarm, factory_farm)

def get_or_add_country_to_db(country_name: str, source="generic") -> Country:
        country_name = normalize_country_name(country_name)
        is_origin = True if source == "origin" else False
        is_destination = True if source == "destination" else False
        if country_name:
            country_instance, _ = Country.objects.get_or_create(
                code= aplha_code_from_country_name(country_name).lower() or NOT_SPECIFIED,
                name= country_name_from_aplha_code(country_name).lower() or NOT_SPECIFIED,
            )
            if not country_instance.is_origin:
                country_instance.is_origin = is_origin
            if not country_instance.is_destination:
                country_instance.is_destination = is_destination
            country_instance.save()
            return country_instance
        else:
            country_instance, _ = Country.objects.get_or_create(
                code = NOT_SPECIFIED,
                name = NOT_SPECIFIED
            )
            if not country_instance.is_origin:
                country_instance.is_origin = is_origin
            if not country_instance.is_destination:
                country_instance.is_destination = is_destination
            country_instance.save()
            
            return country_instance

def get_or_add_gender_to_db(gender: str) -> Gender:
    return get_or_create_model_instance(Gender, gender)

def get_or_add_age_to_db(age_range: str) -> Age:
    age_instance, _ = Age.objects.get_or_create(range= age_range or NOT_SPECIFIED)
    return age_instance


def get_or_add_language_to_db(language_code: str) -> Language:
    language_name_from_code = get_language_name(language_code)
    name = language_name_from_code or NOT_SPECIFIED
    instance, _ = Language.objects.get_or_create(
        code = language_code or NOT_SPECIFIED, 
        name = name.lower()
    )
    return instance

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