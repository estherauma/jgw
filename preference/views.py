from django.shortcuts import render

from core.forms import GenericFilterForm
from preference.repository.preference import (
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