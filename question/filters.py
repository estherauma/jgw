
from typing import Any
from django.db.models import Manager as BaseManager, Q

from users.utils import get_user_destinations, get_user_factories, get_user_organisations


def generic_question_filtered_queryset(
    current_user,
    queryset: BaseManager[Any],
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations = None,
    schemes = None,
    factory_farms = None,
    question_texts = None,
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
        
    if question_texts is None:
        question_texts = []
    
    # current user specific orgs and factories filters
    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)
    
    user_fact_farm_q = Q(preference__factory_farm__in=user_factories) | Q(factory_farm__in=user_factories)
    user_org_q = Q(preference__organisation__in=user_orgs) | Q(organisation__in=user_orgs)
    user_destination_q = Q(preference__destination__in=user_destinations) | Q(destination__in=user_destinations)
    
    user_fact_and_org_q = user_org_q | user_fact_farm_q | user_destination_q
    queryset = queryset.filter(user_fact_and_org_q)
    
    if start_date and end_date:
        queryset = queryset.filter(api_created_at__range=(start_date, end_date))
        
    if destination_countries:
        preference_dest_q = Q(preference__destination__name__in=destination_countries)
        current_model_dest_q = Q(destination__name__in=destination_countries)
        combined_dest_q = preference_dest_q | current_model_dest_q
        queryset = queryset.filter(combined_dest_q)
        
    if origin_countries:
        preference_origin_q = Q(preference__origin__name__in=origin_countries)
        current_model_dest_q = Q(origin__name__in=origin_countries)
        combined_origin_q = preference_origin_q | current_model_dest_q
        queryset = queryset.filter(combined_origin_q)
        
    if organisations:
        preference_organisation_q = Q(preference__organisation__name__in=organisations)
        current_model_dest_q = Q(organisation__name__in=organisations)
        combined_organisation_q = preference_organisation_q | current_model_dest_q
        queryset = queryset.filter(combined_organisation_q)
    
    if factory_farms:
        preference_factory_farm_q = Q(preference__factory_farm__name__in=factory_farms)
        current_model_dest_q = Q(factory_farm__name__in=factory_farms)
        combined_factory_farm_q = preference_factory_farm_q | current_model_dest_q
        queryset = queryset.filter(combined_factory_farm_q)
        
    if question_texts:
        queryset = queryset.filter(
            question_standard__question__translated_text__in=question_texts
        )
        
    
    return queryset


def question_response_filtered_queryset(
    current_user,
    queryset: BaseManager[Any],
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations = None,
    schemes = None,
    factory_farms = None,
    question_texts = None,
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
        
    if question_texts is None:
        question_texts = []
    
    # current user specific orgs and factories filters
    user_factories = get_user_factories(current_user)
    user_orgs = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)
    
    user_fact_farm_q = Q(inline_question__inline_question_standard__preference__factory_farm__in=user_factories) \
        | Q(inline_question__inline_question_standard__factory_farm__in=user_factories)
    user_org_q = Q(inline_question__inline_question_standard__preference__organisation__in=user_orgs) \
        | Q(inline_question__inline_question_standard__organisation__in=user_orgs)
    user_destination_q = Q(inline_question__inline_question_standard__preference__destination__in=user_destinations) \
        | Q(inline_question__inline_question_standard__destination__in=user_destinations)
    
    user_fact_and_org_q = user_org_q | user_fact_farm_q | user_destination_q
    queryset = queryset.filter(user_fact_and_org_q)
    
    if start_date and end_date:
        queryset = queryset.filter(inline_question__inline_question_standard__preference__api_created_at__range=(start_date, end_date))
        
    if destination_countries:
        preference_dest_q = Q(inline_question__inline_question_standard__preference__destination__name__in=destination_countries)
        current_model_dest_q = Q(inline_question__inline_question_standard__destination__name__in=destination_countries)
        combined_dest_q = preference_dest_q | current_model_dest_q
        queryset = queryset.filter(combined_dest_q)
        
    if origin_countries:
        preference_origin_q = Q(inline_question__inline_question_standard__preference__origin__name__in=origin_countries)
        current_model_dest_q = Q(inline_question__inline_question_standard__origin__name__in=origin_countries)
        combined_origin_q = preference_origin_q | current_model_dest_q
        queryset = queryset.filter(combined_origin_q)
        
    if organisations:
        preference_organisation_q = Q(inline_question__inline_question_standard__preference__organisation__name__in=organisations)
        current_model_dest_q = Q(inline_question__inline_question_standard__organisation__name__in=organisations)
        combined_organisation_q = preference_organisation_q | current_model_dest_q
        queryset = queryset.filter(combined_organisation_q)
        
    if factory_farms:
        preference_factory_farm_q = Q(inline_question__inline_question_standard__preference__factory_farm__name__in=factory_farms)
        current_model_dest_q = Q(inline_question__inline_question_standard__factory_farm__name__in=factory_farms)
        combined_factory_farm_q = preference_factory_farm_q | current_model_dest_q
        queryset = queryset.filter(combined_factory_farm_q)
           
    if question_texts:
        queryset = queryset.filter(
            inline_question__question__translated_text__in=question_texts
        )
    
    return queryset