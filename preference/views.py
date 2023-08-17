from django.shortcuts import render
from core.filters import generic_filter_form_parser

from core.forms import GenericFilterForm
from core.logic.file_export import generate_and_export_excel
from preference.repository.preference import (
    get_all_organisations_list,
    preference_stats_for_export,
    preferences_by_age, 
    preferences_by_destination, 
    preferences_by_gender,
    preferences_by_language,
    preferences_by_organisation, 
    preferences_by_origin, 
    preferences_count
)


def user_overview(request):
    if request.method == 'GET':
        filter_form = GenericFilterForm()
        total_user_overview_responses = preferences_count()
        preferences_per_origin_country_responses = preferences_by_origin()
        preferences_per_destination_country_responses = preferences_by_destination()
        preferences_by_age_responses = preferences_by_age()
        preferences_by_gender_responses = preferences_by_gender()
        preferences_by_language_responses = preferences_by_language()
        preferences_by_organisation_responses = preferences_by_organisation()
    
    else:
        filter_form = GenericFilterForm(request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)
        
        total_user_overview_responses = preferences_count(**filters)
        preferences_per_origin_country_responses = preferences_by_origin(**filters)
        preferences_per_destination_country_responses = preferences_by_destination(**filters)
        preferences_by_age_responses = preferences_by_age(**filters)
        preferences_by_gender_responses = preferences_by_gender(**filters)
        preferences_by_language_responses = preferences_by_language(**filters)
        preferences_by_organisation_responses = preferences_by_organisation(**filters)
        
    context = {
        'filter_form': filter_form,
        'total_user_overview_responses': total_user_overview_responses,
        'preferences_by_age': preferences_by_age_responses,
        'preferences_by_gender': preferences_by_gender_responses,
        'preferences_per_origin_country': preferences_per_origin_country_responses,
        'preferences_per_destination_country': preferences_per_destination_country_responses,
        'preferences_selected_user_language': preferences_by_language_responses,
        'work_code_usage': preferences_by_organisation_responses,
    }
    return render(
        request, 
        'preference/user_overview.html',
        context=context
    )
    

def export_preference_stats(request):
    if request.method == 'POST':
        
        filter_form = GenericFilterForm(request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get('organisation', None)
        
        if organisations is None:
            # TODO: otherwise , get all loggedin user's organisations
            organisations = get_all_organisations_list()
        
        export_dict = {
            "all": preference_stats_for_export({**filters, 'organisations': organisations})
        }
        
        for organisation in organisations:
            export_dict[organisation] = preference_stats_for_export({**filters, 'organisations': [organisation]})
            
        return generate_and_export_excel(export_dict) 