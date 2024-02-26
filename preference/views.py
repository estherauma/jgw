from django.shortcuts import render
from core.filters import generic_filter_form_parser

from core.forms import GenericFilterForm
from core.logic.file_export import generate_and_export_excel
from events.repository.bigquery_sws_pasi_repository import get_total_dynamic_link_usage
from preference.repository.preference_repository import (
    cumulative_new_users,
    preference_stats_for_export,
    preferences_by_age,
    preferences_by_destination,
    preferences_by_gender,
    preferences_by_language,
    preferences_by_organisation,
    preferences_by_origin,
    preferences_count,
)
from users.utils import get_user_organisations


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
        pref_cumulative_new_users = cumulative_new_users(current_user=request.user)

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
        pref_cumulative_new_users = cumulative_new_users(**filters, current_user=request.user)

    pasi_downloads = (
        get_total_dynamic_link_usage(current_user=request.user)
        if not request.user.is_anonymous and request.user.role == "SCHEME"
        else 0
    )

    context = {
        "filter_form": filter_form,
        "total_user_overview_responses": total_user_overview_responses,
        "preferences_by_age": preferences_by_age_responses,
        "preferences_by_gender": preferences_by_gender_responses,
        "preferences_per_origin_country": preferences_per_origin_country_responses,
        "preferences_per_destination_country": preferences_per_destination_country_responses,
        "preferences_selected_user_language": preferences_by_language_responses,
        "work_code_usage": preferences_by_organisation_responses,
        "has_orgs": len(get_user_organisations(request.user)) > 0,
        "pasi_downloads": pasi_downloads,
        "pref_cumulative_monthly_new_users": pref_cumulative_new_users,
    }
    return render(request, "preference/user_overview.html", context=context)


def export_preference_stats(request):
    if request.method == "POST":
        filter_form = GenericFilterForm(request=request, data=request.POST)
        if filter_form.is_valid():
            filters = generic_filter_form_parser(filter_form)

        organisations = filters.get("organisations", None)
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
