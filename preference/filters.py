from django.db.models import Manager as BaseManager, Q
from datetime import datetime
from typing import Any
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from users.utils import (
    get_user_destinations,
    get_user_excluded_origin_countries,
    get_user_languages,
    get_user_factories,
    get_user_organisations,
    get_user_start_date,
    get_user_end_date,
    get_user_immigration_status,
)


def preference_filtered_queryset(
    queryset: BaseManager[Any],
    current_user=None,
    show_new_user_data=False,
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations=None,
    schemes=None,
    factory_farms=None,
    immigration_status=None,
):
    user_start_date = get_user_start_date(current_user)
    user_end_date = get_user_end_date(current_user)

    final_start_date = (
        max(start_date, user_start_date)
        if start_date and user_start_date
        else (start_date or user_start_date or APPLICATION_POSSIBLE_START_DATE)
    )
    final_end_date = (
        min(end_date, user_end_date)
        if end_date and user_end_date
        else (end_date or user_end_date or datetime.now().date())
    )

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

    if immigration_status is None:
        immigration_status = []

    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)
    user_languages = get_user_languages(current_user)
    user_excluded_origin_countries = get_user_excluded_origin_countries(current_user)
    user_immigration_status = get_user_immigration_status(current_user)


    preference_filters_q_object = Q()

    if show_new_user_data:
        preference_filters_q_object &= Q(api_created_at__date__range=(final_start_date, final_end_date))

    if organisations:
        preference_filters_q_object &= Q(organisation__name__in=organisations)

    if user_orgs and not organisations:
        preference_filters_q_object &= Q(organisation__in=user_orgs)

    if factory_farms:
        preference_filters_q_object &= Q(factory_farm__name__in=factory_farms)

    if user_factories and not factory_farms:
        preference_filters_q_object &= Q(factory_farm__in=user_factories)

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

    if immigration_status:
        preference_filters_q_object &= Q(immigration_status__name__in=immigration_status)

    if user_immigration_status and not immigration_status:
        preference_filters_q_object &= Q(immigration_status__in=user_immigration_status)

    return queryset.filter(preference_filters_q_object)
