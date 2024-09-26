from datetime import datetime
from typing import Any
from django.db.models import Manager as BaseManager, Q
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE

from users.utils import (
    get_user_destinations,
    get_user_factories,
    get_user_group,
    get_user_organisations,
    get_user_start_date,
    get_user_end_date,
)


def generic_chapters_opened_filtered_queryset(
    current_user,
    queryset: BaseManager[Any],
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations=None,
    schemes=None,
    factory_farms=None,
    sector_of_work=None,
):
    user_start_date = get_user_start_date(current_user)
    user_end_date = get_user_end_date(current_user)
    user_group = get_user_group(current_user)

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

    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)

    chapters_opened_filters_q_object = Q()

    chapters_opened_filters_q_object &= Q(event_created_at__date__range=(final_start_date, final_end_date))

    if user_orgs and "MyVoiceConfig" not in user_group:
        user_org_q = Q(organisation__in=user_orgs)
        chapters_opened_filters_q_object &= user_org_q
    elif "MyVoiceConfig" in user_group:
        user_org_q = Q(destination__in=user_destinations)
        chapters_opened_filters_q_object &= user_org_q

    if user_factories:
        user_fact_farm_q = Q(factory_farm__in=user_factories)
        chapters_opened_filters_q_object &= user_fact_farm_q

    if user_destinations:
        user_destination_q = Q(destination__in=user_destinations)
        chapters_opened_filters_q_object &= user_destination_q

    if destination_countries:
        preference_dest_q = Q(destination__name__in=destination_countries)
        chapters_opened_filters_q_object &= preference_dest_q

    if origin_countries:
        preference_origin_q = Q(origin__name__in=origin_countries)
        chapters_opened_filters_q_object &= preference_origin_q

    if organisations:
        preference_organisation_q = Q(organisation__name__in=organisations)
        chapters_opened_filters_q_object &= preference_organisation_q

    if factory_farms:
        preference_factory_farm_q = Q(factory_farm__name__in=factory_farms)
        chapters_opened_filters_q_object &= preference_factory_farm_q

    if sector_of_work:
        pass

    return queryset.filter(chapters_opened_filters_q_object)


def generic_chapters_feedback_filtered_queryset(
    current_user,
    queryset: BaseManager[Any],
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations=None,
    schemes=None,
    factory_farms=None,
    sector_of_work=None,
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

    # current user specific orgs and factories filters

    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)

    chapters_feedback_filters_q_object = Q()

    # date range filter
    chapters_feedback_filters_q_object &= Q(
        feedback_standard__api_created_at__date__range=(final_start_date, final_end_date)
    )

    # organisation filter
    if user_orgs:
        user_org_q = Q(feedback_standard__organisation__in=user_orgs)
        chapters_feedback_filters_q_object &= user_org_q

    if user_factories:
        user_fact_farm_q = Q(feedback_standard__factory_farm__in=user_factories)
        chapters_feedback_filters_q_object &= user_fact_farm_q

    if user_destinations:
        user_destination_q = Q(feedback_standard__destination__in=user_destinations)
        chapters_feedback_filters_q_object &= user_destination_q

    if destination_countries:
        preference_dest_q = Q(feedback_standard__destination__name__in=destination_countries)
        chapters_feedback_filters_q_object &= preference_dest_q

    if origin_countries:
        preference_origin_q = Q(feedback_standard__origin__name__in=origin_countries)
        chapters_feedback_filters_q_object &= preference_origin_q

    if organisations:
        preference_organisation_q = Q(feedback_standard__organisation__name__in=organisations)
        chapters_feedback_filters_q_object &= preference_organisation_q

    if factory_farms:
        preference_factory_farm_q = Q(feedback_standard__factory_farm__name__in=factory_farms)
        chapters_feedback_filters_q_object &= preference_factory_farm_q

    if sector_of_work:
        pass

    return queryset.filter(chapters_feedback_filters_q_object)


def filter_bigquery_homepage_event_data(queryset, **filters):
    if filters.get("start_date"):
        queryset = queryset.filter(event_date__gte=filters["start_date"])

    if filters.get("end_date"):
        queryset = queryset.filter(event_date__lte=filters["end_date"])

    if filters.get("destination_countries"):
        queryset = queryset.filter(destination__name__in=filters["destination_countries"])

    if filters.get("organisations"):
        queryset = queryset.filter(organisation__name__in=filters["organisations"])

    return queryset
