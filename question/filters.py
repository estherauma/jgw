from datetime import datetime
from typing import Any
from django.db.models import Manager as BaseManager, Q
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE

from users.utils import (
    get_user_destinations,
    get_user_factories,
    get_user_organisations,
    get_user_start_date,
    get_user_end_date,
    get_user_immigration_status,
)


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
    sector_of_work=None,
    immigration_status=None,
    show_new_user_data=False,
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

    if immigration_status is None:
        immigration_status = []

    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)
    user_immigration_status = get_user_immigration_status(current_user)

    generic_question_filters_q_object = Q()

    if user_orgs:
        user_org_names = [org.name for org in user_orgs]
        user_org_q = Q(org_info__name__in=user_org_names)
        generic_question_filters_q_object &= user_org_q

    if user_factories:
        user_fact_farm_q = Q(factory_farm__in=user_factories)
        generic_question_filters_q_object &= user_fact_farm_q

    if user_destinations:
        user_destination_q = Q(destination__in=user_destinations)
        generic_question_filters_q_object &= user_destination_q

    if start_date and end_date:
        generic_question_filters_q_object &= Q(api_created_at__range=(start_date, end_date))

    if destination_countries:
        preference_dest_q = Q(destination__name__in=destination_countries)
        generic_question_filters_q_object &= preference_dest_q

    if origin_countries:
        preference_origin_q = Q(origin__name__in=origin_countries)
        generic_question_filters_q_object &= preference_origin_q

    if organisations:
        preference_organisation_q = Q(org_info__name__in=organisations)
        generic_question_filters_q_object &= preference_organisation_q

    if factory_farms:
        preference_factory_farm_q = Q(factory_farm__name__in=factory_farms)
        generic_question_filters_q_object &= preference_factory_farm_q

    if sector_of_work:
        pass

    if immigration_status:
        immigration_status_q = Q(immigration_status__name__in=immigration_status)
        generic_question_filters_q_object &= immigration_status_q
    elif user_immigration_status:
        user_immigration_status_q = Q(immigration_status__in=user_immigration_status)
        generic_question_filters_q_object &= user_immigration_status_q

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
    sector_of_work=None,
    immigration_status=None,
    show_new_user_data=False,
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
    user_immigration_status = get_user_immigration_status(current_user)

    question_response_filters_q_object = Q()

    if show_new_user_data is False:

        question_response_filters_q_object &= Q(
            inline_question__inline_question_standard__api_created_at__range=(
                final_start_date,
                final_end_date,
            )
        )

    if user_factories:
        user_fact_farm_q = Q(
            inline_question__inline_question_standard__preference__factory_farm__in=user_factories
        ) | Q(inline_question__inline_question_standard__factory_farm__in=user_factories)

        question_response_filters_q_object &= user_fact_farm_q

    if user_orgs:
        organisation_q_objects = Q()
        user_org_names = [org.name for org in user_orgs]
        if "Evergreen" in user_org_names:
            organisation_q_objects |= Q(organisation_inline_question="evergreen") & Q(
                inline_question__inline_question_standard__destination__name="malaysia"
            ) & Q(
                inline_question__inline_question_standard__org_info__name="Evergreen"
            )
        if "Dashboard Demo" in user_org_names:
            organisation_q_objects |= Q(organisation_inline_question="myvoice") & Q(
                inline_question__inline_question_standard__destination__name="malaysia"
            ) & Q(
                inline_question__inline_question_standard__org_info__name="Dashboard Demo"
            )

        other_organisations = [org for org in user_org_names if org not in {"Evergreen", "Dashboard Demo"}]
        if other_organisations:
            organisation_q_objects |= Q(
                inline_question__inline_question_standard__org_info__name__in=other_organisations
            )
        question_response_filters_q_object &= organisation_q_objects

    if user_destinations:
        user_destination_q = Q(inline_question__inline_question_standard__destination__in=user_destinations)
        question_response_filters_q_object &= user_destination_q

    if destination_countries:
        current_model_dest_q = Q(
            inline_question__inline_question_standard__destination__name__in=destination_countries
        )

        question_response_filters_q_object &= current_model_dest_q

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
        organisation_q_objects = Q()
        if "Evergreen" in organisations:
            organisation_q_objects |= Q(organisation_inline_question="evergreen") & Q(
                inline_question__inline_question_standard__destination__name="malaysia"
            ) & Q(
                inline_question__inline_question_standard__org_info__name="Evergreen"
            )
        if "Dashboard Demo" in organisations:
            organisation_q_objects |= Q(organisation_inline_question="myvoice") & Q(
                inline_question__inline_question_standard__destination__name="malaysia"
            ) & Q(
                inline_question__inline_question_standard__org_info__name="Dashboard Demo"
            )

        other_organisations = [org for org in organisations if org not in {"Evergreen", "Dashboard Demo"}]
        if other_organisations:
            organisation_q_objects |= Q(
                inline_question__inline_question_standard__org_info__name__in=other_organisations
            )

        question_response_filters_q_object &= organisation_q_objects

    if factory_farms:
        preference_factory_farm_q = Q(
            inline_question__inline_question_standard__preference__factory_farm__name__in=factory_farms
        )
        current_model_dest_q = Q(
            inline_question__inline_question_standard__factory_farm__name__in=factory_farms
        )
        combined_factory_farm_q = preference_factory_farm_q | current_model_dest_q
        question_response_filters_q_object &= combined_factory_farm_q

    if sector_of_work:
        pass

    if immigration_status:
        immigration_status_q = Q(
            inline_question__inline_question_standard__preference__immigration_status__name__in=immigration_status
        ) | Q(inline_question__inline_question_standard__immigration_status__name__in=immigration_status)
        question_response_filters_q_object &= immigration_status_q
    elif user_immigration_status:
        user_immigration_status_q = Q(
            inline_question__inline_question_standard__preference__immigration_status__in=user_immigration_status
        ) | Q(inline_question__inline_question_standard__immigration_status__in=user_immigration_status)
        question_response_filters_q_object &= user_immigration_status_q

    return queryset.filter(question_response_filters_q_object)


def message_data_sent_filtered_queryset(
    current_user,
    queryset: BaseManager[Any],
    show_new_user_data=False,
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations=None,
    schemes=None,
    factory_farms=None,
    sector_of_work=None,
    immigration_status=None,
):
    user_start_date = get_user_start_date(current_user)
    user_end_date = get_user_end_date(current_user)
    user_destinations = get_user_destinations(current_user)
    user_orgs = get_user_organisations(current_user)

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

    if organisations is None:
        organisations = []
    if current_user.is_superuser:
        user_destinations = []
        user_orgs = []

    message_data_push_filters_q_object = Q()

    message_data_push_filters_q_object &= Q(message_date__range=(final_start_date, final_end_date))

    if user_destinations:
        message_data_push_filters_q_object &= Q(destination__in=user_destinations)
    if destination_countries:
        message_data_push_filters_q_object &= Q(destination__name__in=destination_countries)

    if user_orgs:
        message_data_push_filters_q_object &= Q(organisation__in=user_orgs)
    if organisations:
        message_data_push_filters_q_object &= Q(organisation__name__in=organisations)

    return queryset.filter(message_data_push_filters_q_object)
