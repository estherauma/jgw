from django.db.models import Manager as BaseManager, Q
from typing import Any

from users.utils import get_user_destinations, get_user_factories, get_user_organisations



def preference_filtered_queryset(
    queryset: BaseManager[Any],
    current_user=None,
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations = None,
    schemes = None,
    factory_farms = None
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
    
    queryset = queryset.filter(
        Q(organisation__in=user_orgs) | Q(factory_farm__in = user_factories) | Q(destination__in=user_destinations)
    )
    
    if start_date and end_date:
        queryset = queryset.filter(api_created_at__range=(start_date, end_date))
        
    if destination_countries:
        current_model_dest_q = Q(destination__name__in=destination_countries) \
            | Q(destination__country_states__name__in=destination_countries)
        queryset = queryset.filter(current_model_dest_q)
        
    if origin_countries:
        current_model_dest_q = Q(origin__name__in=origin_countries) \
            | Q(origin__country_states__name__in=origin_countries)
        queryset = queryset.filter(current_model_dest_q)
        
    if organisations:
        current_model_dest_q = Q(organisation__name__in=organisations)
        queryset = queryset.filter(current_model_dest_q)
    
    if factory_farms:
        current_model_dest_q = Q(factory_farm__name__in=factory_farms)
        queryset = queryset.filter(current_model_dest_q)
        
    
    return queryset