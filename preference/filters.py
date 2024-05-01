from django.db.models import Manager as BaseManager, Q
from typing import Any
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from users.utils import (
    get_user_destinations,
    get_user_excluded_origin_countries,
    get_user_languages,
    get_user_factories,
    get_user_organisations,
)


def preference_filtered_queryset(
    queryset: BaseManager[Any],
    current_user=None,
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations=None,
    schemes=None,
    factory_farms=None,
):
    
    if start_date is None:
        start_date = APPLICATION_POSSIBLE_START_DATE
        
    if destination_countries is None:
        destination_countries = []

    if origin_countries is None:
        origin_countries = []

    if organisations is None:
        organisations = []

    if schemes is None:
        schemes = []

    if factory_farms is None:
        factory_farms = []

    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)
    user_languages = get_user_languages(current_user)
    user_excluded_origin_countries = get_user_excluded_origin_countries(current_user)

    preference_filters_q_object = Q()

    # date range filter
    if start_date and end_date:
        preference_filters_q_object &= Q(api_created_at__range=(start_date, end_date))

    # organisation filter
    if organisations:
        preference_filters_q_object &= Q(organisation__name__in=organisations)

    if user_orgs and not organisations:
        preference_filters_q_object &= Q(organisation__in=user_orgs)

    # organisation factories
    if factory_farms:
        preference_filters_q_object &= Q(factory_farm__name__in=factory_farms)

    if user_factories and not factory_farms:
        preference_filters_q_object &= Q(factory_farm__in=user_factories)

    # destinations
    if destination_countries:
        preference_filters_q_object &= Q(destination__name__in=destination_countries)

    if user_destinations and not destination_countries:
        preference_filters_q_object &= Q(destination__in=user_destinations)

    if user_languages:
        preference_filters_q_object &= Q(language__in=user_languages)

    if user_excluded_origin_countries and not origin_countries:
        preference_filters_q_object &= ~Q(origin__in=user_excluded_origin_countries)

    if origin_countries:
        preference_filters_q_object &= Q(origin__name__in=origin_countries)

    # exclude disabled sectors of work
    return queryset.filter(preference_filters_q_object)
