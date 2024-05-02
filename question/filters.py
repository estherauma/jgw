from datetime import datetime
from typing import Any
from django.db.models import Manager as BaseManager, Q
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE

from users.utils import get_user_destinations, get_user_factories, get_user_organisations


def generic_question_filtered_queryset(
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
    if start_date is None:
        start_date = APPLICATION_POSSIBLE_START_DATE

    if end_date is None:
        end_date = datetime.now().date()
        
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

    generic_question_filters_q_object = Q()

    if user_orgs:
        user_org_q = Q(preference__organisation__in=user_orgs) | Q(organisation__in=user_orgs)
        generic_question_filters_q_object &= user_org_q

    if user_factories:
        user_fact_farm_q = Q(preference__factory_farm__in=user_factories) | Q(factory_farm__in=user_factories)
        generic_question_filters_q_object &= user_fact_farm_q

    if user_destinations:
        user_destination_q = Q(preference__destination__in=user_destinations) | Q(
            destination__in=user_destinations
        )
        generic_question_filters_q_object &= user_destination_q

    if start_date and end_date:
        generic_question_filters_q_object &= Q(api_created_at__range=(start_date, end_date))

    if destination_countries:
        preference_dest_q = Q(preference__destination__name__in=destination_countries) | Q(
            destination__name__in=destination_countries
        )
        generic_question_filters_q_object &= preference_dest_q

    if origin_countries:
        preference_origin_q = Q(preference__origin__name__in=origin_countries) | Q(
            origin__name__in=origin_countries
        )
        generic_question_filters_q_object &= preference_origin_q

    if organisations:
        preference_organisation_q = Q(preference__organisation__name__in=organisations) | Q(
            organisation__name__in=organisations
        )
        generic_question_filters_q_object &= preference_organisation_q

    if factory_farms:
        preference_factory_farm_q = Q(preference__factory_farm__name__in=factory_farms) | Q(
            factory_farm__name__in=factory_farms
        )
        generic_question_filters_q_object &= preference_factory_farm_q

    return queryset.filter(generic_question_filters_q_object)


def question_response_filtered_queryset(
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

    question_response_filters_q_object = Q()

    if user_factories:
        user_fact_farm_q = Q(
            inline_question__inline_question_standard__preference__factory_farm__in=user_factories
        ) | Q(inline_question__inline_question_standard__factory_farm__in=user_factories)

        question_response_filters_q_object &= user_fact_farm_q

    if user_orgs:
        user_org_q = Q(inline_question__inline_question_standard__preference__organisation__in=user_orgs) | Q(
            inline_question__inline_question_standard__organisation__in=user_orgs
        )
        question_response_filters_q_object &= user_org_q

    if user_destinations:
        user_destination_q = Q(
            inline_question__inline_question_standard__preference__destination__in=user_destinations
        ) | Q(inline_question__inline_question_standard__destination__in=user_destinations)
        question_response_filters_q_object &= user_destination_q

    if start_date and end_date:
        question_response_filters_q_object &= Q(
            inline_question__inline_question_standard__preference__api_created_at__range=(
                start_date,
                end_date,
            )
        )

    if destination_countries:
        preference_dest_q = Q(
            inline_question__inline_question_standard__preference__destination__name__in=destination_countries
        ) | Q(
            inline_question__inline_question_standard__preference__destination__country_states__name__in=destination_countries
        )
        current_model_dest_q = Q(
            inline_question__inline_question_standard__destination__name__in=destination_countries
        ) | Q(
            inline_question__inline_question_standard__destination__country_states__name__in=destination_countries
        )
        combined_dest_q = preference_dest_q | current_model_dest_q
        question_response_filters_q_object &= combined_dest_q

    if origin_countries:
        preference_origin_q = Q(
            inline_question__inline_question_standard__preference__origin__name__in=origin_countries
        ) | Q(
            inline_question__inline_question_standard__preference__origin__country_states__name__in=destination_countries
        )
        current_model_dest_q = Q(
            inline_question__inline_question_standard__origin__name__in=origin_countries
        ) | Q(
            inline_question__inline_question_standard__origin__country_states__name__in=destination_countries
        )
        combined_origin_q = preference_origin_q | current_model_dest_q
        question_response_filters_q_object &= combined_origin_q

    if organisations:
        preference_organisation_q = Q(
            inline_question__inline_question_standard__preference__organisation__name__in=organisations
        )
        current_model_dest_q = Q(
            inline_question__inline_question_standard__organisation__name__in=organisations
        )
        combined_organisation_q = preference_organisation_q | current_model_dest_q
        question_response_filters_q_object &= combined_organisation_q

    if factory_farms:
        preference_factory_farm_q = Q(
            inline_question__inline_question_standard__preference__factory_farm__name__in=factory_farms
        )
        current_model_dest_q = Q(
            inline_question__inline_question_standard__factory_farm__name__in=factory_farms
        )
        combined_factory_farm_q = preference_factory_farm_q | current_model_dest_q
        question_response_filters_q_object &= combined_factory_farm_q

    return queryset.filter(question_response_filters_q_object)
