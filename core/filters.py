from typing import Any
from django.db.models import Manager as BaseManager, Q


def generic_filter_form_parser(filter_form):
        start_date = filter_form.cleaned_data['start_date']
        end_date = filter_form.cleaned_data['end_date']
        destinations = filter_form.cleaned_data['destination']
        origins = filter_form.cleaned_data['origin']
        
        return (start_date, end_date, origins, destinations)
            
def generic_filtered_queryset(
    queryset: BaseManager[Any],
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
):
    if destination_countries is None:
        destination_countries = []
    
    if origin_countries is None:
        origin_countries = []
    
    
    if start_date and end_date:
        queryset = queryset.filter(api_created_at__range=(start_date, end_date))
        
    if destination_countries:
        preference_dest_q = Q(preference__destination__in=destination_countries)
        messaging_dest_q = Q(destination__in=destination_countries)
        combined_dest_q = preference_dest_q | messaging_dest_q
        
        queryset = queryset.filter(combined_dest_q)
        
    if origin_countries:
        preference_origin_q = Q(preference__origin__in=origin_countries)
        messaging_origin_q = Q(origin__in=origin_countries)
        combined_origin_q = preference_origin_q | messaging_origin_q
        
        queryset = queryset.filter(combined_origin_q)
    
    return queryset