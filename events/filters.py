from typing import Any
from django.db.models import Manager as BaseManager, Q

from users.utils import get_user_destinations, get_user_factories, get_user_organisations


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

    # current user specific orgs and factories filters

    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)

    chapters_opened_filters_q_object = Q()

    # date range filter
    if start_date and end_date:
        chapters_opened_filters_q_object &= Q(event_created_at__range=(start_date, end_date))

    # organisation filter
    if user_orgs:
        user_org_q = Q(preference__organisation__in=user_orgs) | Q(organisation__in=user_orgs)
        chapters_opened_filters_q_object &= user_org_q

    if user_factories:
        user_fact_farm_q = Q(preference__factory_farm__in=user_factories) | Q(factory_farm__in=user_factories)
        chapters_opened_filters_q_object &= user_fact_farm_q

    if user_destinations:
        user_destination_q = Q(preference__destination__in=user_destinations) | Q(
            destination__in=user_destinations
        )
        chapters_opened_filters_q_object &= user_destination_q

    if destination_countries:
        preference_dest_q = Q(preference__destination__name__in=destination_countries) | Q(
            destination__name__in=destination_countries
        )
        chapters_opened_filters_q_object &= preference_dest_q

    if origin_countries:
        preference_origin_q = Q(preference__origin__name__in=origin_countries) | Q(
            origin__name__in=origin_countries
        )
        chapters_opened_filters_q_object &= preference_origin_q

    if organisations:
        preference_organisation_q = Q(preference__organisation__name__in=organisations) | Q(
            organisation__name__in=organisations
        )
        chapters_opened_filters_q_object &= preference_organisation_q

    if factory_farms:
        preference_factory_farm_q = Q(preference__factory_farm__name__in=factory_farms) | Q(
            factory_farm__name__in=factory_farms
        )
        chapters_opened_filters_q_object &= preference_factory_farm_q

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

    # current user specific orgs and factories filters

    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)

    chapters_feedback_filters_q_object = Q()

    # # date range filter
    if start_date and end_date:
        chapters_feedback_filters_q_object &= Q(
            feedback_standard__api_created_at__range=(start_date, end_date)
        )

    # # organisation filter
    if user_orgs:
        user_org_q = Q(feedback_standard__preference__organisation__in=user_orgs) | Q(
            feedback_standard__organisation__in=user_orgs
        )
        chapters_feedback_filters_q_object &= user_org_q

    if user_factories:
        user_fact_farm_q = Q(feedback_standard__preference__factory_farm__in=user_factories) | Q(
            feedback_standard__factory_farm__in=user_factories
        )
        chapters_feedback_filters_q_object &= user_fact_farm_q

    if user_destinations:
        user_destination_q = Q(feedback_standard__preference__destination__in=user_destinations) | Q(
            feedback_standard__destination__in=user_destinations
        )
        chapters_feedback_filters_q_object &= user_destination_q

    if destination_countries:
        preference_dest_q = Q(feedback_standard__preference__destination__name__in=destination_countries) | Q(
            feedback_standard__destination__name__in=destination_countries
        )
        chapters_feedback_filters_q_object &= preference_dest_q

    if origin_countries:
        preference_origin_q = Q(feedback_standard__preference__origin__name__in=origin_countries) | Q(
            feedback_standard__origin__name__in=origin_countries
        )
        chapters_feedback_filters_q_object &= preference_origin_q

    if organisations:
        preference_organisation_q = Q(
            feedback_standard__preference__organisation__name__in=organisations
        ) | Q(feedback_standard__organisation__name__in=organisations)
        chapters_feedback_filters_q_object &= preference_organisation_q

    if factory_farms:
        preference_factory_farm_q = Q(
            feedback_standard__preference__factory_farm__name__in=factory_farms
        ) | Q(feedback_standard__factory_farm__name__in=factory_farms)
        chapters_feedback_filters_q_object &= preference_factory_farm_q

    return queryset.filter(chapters_feedback_filters_q_object)
