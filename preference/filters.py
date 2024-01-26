from django.db.models import Manager as BaseManager, Q
from typing import Any

from users.utils import (
    get_user_destinations,
    get_user_excepted_languages,
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
    user_excepted_languages = get_user_excepted_languages(current_user)

    preference_filters_q_object = Q()

    if user_orgs:
        preference_filters_q_object &= Q(organisation__in=user_orgs)

    if user_factories:
        preference_filters_q_object &= Q(factory_farm__in=user_factories)

    if user_destinations:
        preference_filters_q_object &= Q(destination__in=user_destinations)

    if user_excepted_languages:
        preference_filters_q_object &= ~Q(language__in=user_excepted_languages)

    if start_date and end_date:
        preference_filters_q_object &= Q(api_created_at__range=(start_date, end_date))

    if destination_countries:
        current_model_dest_q = Q(destination__name__in=destination_countries) | Q(
            destination__country_states__name__in=destination_countries
        )
        preference_filters_q_object &= current_model_dest_q

    if origin_countries:
        current_model_origin_q = Q(origin__name__in=origin_countries) | Q(
            origin__country_states__name__in=origin_countries
        )
        preference_filters_q_object &= current_model_origin_q

    if organisations:
        preference_filters_q_object &= Q(organisation__name__in=organisations)

    if factory_farms:
        preference_filters_q_object &= Q(factory_farm__name__in=factory_farms)

    return queryset.filter(preference_filters_q_object)
