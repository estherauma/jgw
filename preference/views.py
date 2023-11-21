from django.shortcuts import render
from core.filters import generic_filter_form_parser

from core.forms import GenericFilterForm
from core.logic.file_export import generate_and_export_excel
from preference.models import SwsCountry
from preference.repository.preference_repository import (
    get_all_organisations_list,
    preference_stats_for_export,
    preferences_by_age,
    preferences_by_destination,
    preferences_by_gender,
    preferences_by_language,
    preferences_by_organisation,
    preferences_by_origin,
    preferences_count,
)
from users.utils import get_user_organisations, get_user_destinations


def user_overview(request):
    if request.method == "GET":
        filter_form = GenericFilterForm(request=request)
        total_user_overview_responses = preferences_count(current_user=request.user)
        preferences_per_origin_country_responses = preferences_by_origin(current_user=request.user)
        preferences_per_destination_country_responses = preferences_by_destination(current_user=request.user)
        preferences_by_age_responses = preferences_by_age(current_user=request.user)
        preferences_by_gender_responses = preferences_by_gender(current_user=request.user)
        preferences_by_language_responses = preferences_by_language(current_user=request.user)
        preferences_by_organisation_responses = preferences_by_organisation(current_user=request.user)

    else:
        filter_form = GenericFilterForm(request=request, data=request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        total_user_overview_responses = preferences_count(**filters, current_user=request.user)
        preferences_per_origin_country_responses = preferences_by_origin(**filters, current_user=request.user)
        preferences_per_destination_country_responses = preferences_by_destination(
            **filters, current_user=request.user
        )
        preferences_by_age_responses = preferences_by_age(**filters, current_user=request.user)
        preferences_by_gender_responses = preferences_by_gender(**filters, current_user=request.user)
        preferences_by_language_responses = preferences_by_language(**filters, current_user=request.user)
        preferences_by_organisation_responses = preferences_by_organisation(
            **filters, current_user=request.user
        )

    is_user_countries_in_sws = SwsCountry.objects.filter(
        country__in=get_user_destinations(request.user)
    ).exists()

    context = {
        "filter_form": filter_form,
        "total_user_overview_responses": total_user_overview_responses,
        "preferences_by_age": preferences_by_age_responses,
        "preferences_by_gender": preferences_by_gender_responses,
        "preferences_per_origin_country": preferences_per_origin_country_responses,
        "preferences_per_destination_country": preferences_per_destination_country_responses,
        "preferences_selected_user_language": preferences_by_language_responses,
        "work_code_usage": preferences_by_organisation_responses,
        "is_user_countries_in_sws": is_user_countries_in_sws,
    }
    return render(request, "preference/user_overview.html", context=context)


def export_preference_stats(request):
    if request.method == "POST":

        filter_form = GenericFilterForm(request=request, data=request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get("organisation", None)
        if organisations is None:
            user_orgs = get_user_organisations(request.user)
            organisations = [getattr(org, "name") for org in user_orgs]

        export_dict = {
            "all": preference_stats_for_export(
                {**filters, "organisations": organisations, "current_user": request.user}
            )
        }

        for organisation in organisations:
            export_dict[organisation] = preference_stats_for_export(
                {**filters, "organisations": [organisation], "current_user": request.user}
            )

        return generate_and_export_excel(export_dict, "preference_stats")
