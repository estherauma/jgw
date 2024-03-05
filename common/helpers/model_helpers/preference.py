from django.db.models import Q, Case, When, Value, CharField, F
from django.db import transaction
from typing import Union

from common.const.value_const import NOT_SPECIFIED
from common.custom_libs.language_codes import get_language_name
from common.custom_libs.pycountry import aplha_code_from_country_name, country_name_from_aplha_code
from common.helpers.model_helpers.get_create import get_or_create_model_instance
from common.helpers.preference_helpers.country import normalize_country_name
from common.helpers.preference_helpers.gender import normalize_gender_name
from common.helpers.preference_helpers.language import normalize_laguage_name
from common.helpers.preference_helpers.organisation import normalize_organisation_name
from preference.models import (
    Age,
    Country,
    CountryState,
    FactoryFarm,
    Gender,
    Language,
    LocationOfPotentialWork,
    Organisation,
    OrganisationSector,
    Route,
    SectorOfWork,
)


def get_or_add_organisation_sector_to_db(organisation_sector: str) -> OrganisationSector:
    return get_or_create_model_instance(OrganisationSector, organisation_sector)


def get_or_add_organisation_to_db(organisation_name: str) -> Organisation:
    normalized_organisation_name = normalize_organisation_name(organisation_name)
    return get_or_create_model_instance(Organisation, normalized_organisation_name)


def get_or_add_factory_farm_to_db(factory_farm: str) -> FactoryFarm:
    return get_or_create_model_instance(FactoryFarm, factory_farm)


def get_or_add_country_state_to_db(country_state_name: str) -> CountryState:
    country_instance, _ = CountryState.objects.get_or_create(name=country_state_name or NOT_SPECIFIED)
    return country_instance


def get_or_add_location_of_potential_work_to_db(country_name: str) -> LocationOfPotentialWork:
    country_name = normalize_country_name(country_name)

    country_code = aplha_code_from_country_name(country_name).lower() or NOT_SPECIFIED
    real_country_name = country_name_from_aplha_code(country_code).lower() or NOT_SPECIFIED

    location_of_potential_work_instance, _ = LocationOfPotentialWork.objects.get_or_create(
        name=real_country_name, code=country_code
    )
    return location_of_potential_work_instance


def get_or_add_country_to_db(country_name: str, source="generic") -> Country:
    country_name = normalize_country_name(country_name)
    is_origin = True if source == "origin" else False
    is_destination = True if source == "destination" else False
    if country_name:
        country_code = aplha_code_from_country_name(country_name).lower() or NOT_SPECIFIED
        real_country_name = country_name_from_aplha_code(country_code).lower() or NOT_SPECIFIED
        try:
            country_instance = Country.objects.get(name__iexact=real_country_name, code__iexact=country_code)
        except Country.DoesNotExist:
            country_instance = Country.objects.create(
                code=country_code,
                name=real_country_name,
                api_value=country_name,
                is_origin=is_origin,
                is_destination=is_destination,
            )
            return country_instance

        if is_origin and not country_instance.is_origin:
            country_instance.is_origin = True
            country_instance.save()
        if is_destination and not country_instance.is_destination:
            country_instance.is_destination = True
            country_instance.save()

        return country_instance

    else:
        country_instance, _ = Country.objects.get_or_create(
            code=NOT_SPECIFIED,
            name=NOT_SPECIFIED,
            defaults={"is_origin": is_origin, "is_destination": is_destination},
        )
        return country_instance


def get_or_add_gender_to_db(gender: str) -> Gender:
    return get_or_create_model_instance(Gender, normalize_gender_name(gender))


def get_or_add_age_to_db(age_range: str) -> Age:
    age_instance, _ = Age.objects.get_or_create(range=age_range or NOT_SPECIFIED)
    return age_instance


def get_or_add_language_to_db(language_code: str) -> Language:
    language_name_from_code = normalize_laguage_name(get_language_name(language_code))
    name = language_name_from_code or NOT_SPECIFIED
    instance, _ = Language.objects.get_or_create(code=language_code or NOT_SPECIFIED, name=name.lower())
    return instance


def get_or_add_route_to_db(route_name: str) -> Route:
    return get_or_create_model_instance(Route, route_name)


def add_sector_of_work_to_db(sectors_of_work: Union[str, list[str]]) -> list[SectorOfWork]:
    sector_list = []

    if not sectors_of_work:
        sector, _ = SectorOfWork.objects.get_or_create(name=NOT_SPECIFIED)
        sector_list.append(sector)
        return sector_list

    if isinstance(sectors_of_work, str):
        sector, _ = SectorOfWork.objects.get_or_create(name=sectors_of_work.strip().lower())
        sector_list.append(sector)
        return sector_list

    for sector_name in sectors_of_work:
        sector, _ = SectorOfWork.objects.get_or_create(name=sector_name.strip().lower())
        sector_list.append(sector)
    return sector_list


def get_countries_without_excluded_names(
    filter, countries_to_exclude=["test-state", "tstd", "tstl", "viet nam"]
):
    exclude_query = Q()
    for country_name in countries_to_exclude:
        exclude_query |= Q(name=country_name)

    return Country.objects.filter(**filter).exclude(exclude_query).order_by("name")


def get_unique_langaues_list():
    lang_list = []
    language_list = (
        Language.objects.annotate(
            new_translated_name=Case(
                When(
                    translated_name="burma",
                    then=Value("burmese"),
                ),
                default=F("translated_name"),
                output_field=CharField(),
            )
        )
        .values_list("new_translated_name", flat=True)
        .distinct()
    )
    for language in language_list:
        lang = Language.objects.filter(translated_name=language).first()
        lang_list.append(lang)
    return lang_list


def make_language_queryset_list_unique(language_list):
    lang_list = []
    new_language_list = (
        language_list.annotate(
            new_translated_name=Case(
                When(
                    translated_name="burma",
                    then=Value("burmese"),
                ),
                default=F("translated_name"),
                output_field=CharField(),
            )
        )
        .values_list("new_translated_name", flat=True)
        .distinct()
    )

    for language in new_language_list:
        lang = Language.objects.filter(translated_name=language).first()
        lang_list.append(lang)
    return lang_list
