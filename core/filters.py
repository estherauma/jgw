from typing import Any
from django.db.models import Manager as BaseManager, Q



def create_generic_filters_dictionary(
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations=None,
    factory_farms=None,
):
    return {
        "start_date": start_date,
        "end_date": end_date,
        "destination_countries": destination_countries,
        "origin_countries": origin_countries,
        "organisations": organisations,
        "factory_farms": factory_farms,
    }
    
def generic_filter_form_parser(filter_form):
        start_date = filter_form.cleaned_data['start_date']
        end_date = filter_form.cleaned_data['end_date']
        destinations = filter_form.cleaned_data['destination']
        origins = filter_form.cleaned_data['origin']
        organisations = filter_form.cleaned_data['organisation']
        factory_farms = filter_form.cleaned_data['factory_farm']
        
        return create_generic_filters_dictionary(
            start_date = start_date,
            end_date = end_date,
            destination_countries = destinations,
            origin_countries = origins,
            organisations = organisations,
            factory_farms = factory_farms,
        )
            
def generic_filtered_queryset(
    queryset: BaseManager[Any],
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations = None,
    schemes = None,
    factory_farms = None,
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
        
    
    return queryset