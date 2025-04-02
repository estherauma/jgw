from collections import defaultdict
from datetime import datetime
from django.db.models import Case, When, Value, CharField, F, Count
from django.db.models.functions import Cast, Substr, Length
from django.db.models import Q
from django.db.models.functions import TruncMonth
from common.const.value_const import ACCESS_CODE_MAPPING, APPLICATION_POSSIBLE_START_DATE, PUBLIC_USER_DATA_START_DATE
from common.helpers.preference_helpers.gender import normalize_gender_name

from common.helpers.preference_helpers.organisation import format_org_name_from_display
from common.utils.strings import format_thousands_with_commas
from preference.filters import preference_filtered_queryset_for_active_users_data, preference_filtered_queryset_for_new_user_data
from preference.models import Organisation, Preference, PreferenceHistory
from events.models import BigqueryHomepageEventData

from django.db.models import Count
from events.models import UserLocation


def preferences_count(**filters):
    base_queryset = Preference.objects.all()
   
    preferences_count_queryset = preference_filtered_queryset_for_new_user_data(
        queryset=base_queryset, 
        **filters
    )

    return format_thousands_with_commas(preferences_count_queryset.count())


def preferences_by_age(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_age_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )

    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_age_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_age_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )

    age_counts = (
        preferences_age_queryset.values("age__translated_range")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    labels = [age["age__translated_range"].title() for age in age_counts]
    counts = [age["total"] for age in age_counts]
    group_mapping = {
        "60+": ["60+"],
        "51-60": ["51-60"],
        "41-50": ["41-50", "40+"],
        "31-40": ["31-35", "36-40", "31-40", "36 - 40", "31 - 35"],
        "21-30": ["21-25", "21-30", "26-30", "21 - 25"],
        "18-20": ["15-18", "15-20", "18-20", "19-20", "15 - 20"],
        "15-17": ["15-17"],
    }

    combined_values = {group: 0 for group in group_mapping}
    combined_values["PREFER NOT TO ANSWER".title()] = 0
    for label, value in zip(labels, counts):
        for group, label_list in group_mapping.items():
            if label in label_list:
                combined_values[group] += value
                break
        else:
            if label == "PREFER NOT TO ANSWER".title() or label == "PREFERNOTTOANSWER".title():
                combined_values["PREFER NOT TO ANSWER".title()] += value
    final_labels = []
    final_counts = []
    for group, value in combined_values.items():
        final_labels.append(group)
        final_counts.append(value)

    return {"labels": final_labels, "counts": final_counts}


def preferences_by_gender(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_gender_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_gender_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )

    else:
        preferences_gender_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )

    gender_counts = (
        preferences_gender_queryset.values("gender__translated_name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    label_sums = defaultdict(int)
    for gender in gender_counts:
        normalized_label = normalize_gender_name(gender["gender__translated_name"]).title()
        label_sums[normalized_label] += gender["total"]

    summed_labels = list(label_sums.keys())
    summed_counts = list(label_sums.values())

    return {"labels": summed_labels, "counts": summed_counts}


def preferences_by_origin(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_origin_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_origin_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_origin_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    preferences_origin_queryset = preferences_origin_queryset.annotate(
        normalized_origin=Case(
            When(origin__name__iexact="phillippines", then=Value("Philippines")),
            When(origin__name__iexact="philippines", then=Value("Philippines")),
            When(origin__name__iexact="russian federation", then=Value("russia")),
            When(origin__name__iexact="republic of moldova", then=Value("moldova")),
            When(origin__name__iexact="sri-lanka", then=Value("sri lanka")),
            When(origin__name__iexact="pdr", then=Value("republic of laos")),
            When(origin__name__iexact="laos", then=Value("republic of laos")),
            default=F("origin__name"),
            output_field=CharField(),
        )
    )

    origin_counts = (
        preferences_origin_queryset.values("normalized_origin").annotate(total=Count("id")).order_by("-total")
    )

    labels = [
        origin["normalized_origin"].title()
        for origin in origin_counts
        if origin["normalized_origin"] is not None
    ]
    counts = [origin["total"] for origin in origin_counts]

    return {"labels": labels, "counts": counts}


def preferences_by_destination(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_destination_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        # Get base queryset from homepage events
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_destination_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_destination_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    destination_counts = (
        preferences_destination_queryset.values("destination__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    labels = [destination["destination__name"].title() for destination in destination_counts]
    counts = [destination["total"] for destination in destination_counts]

    return {"labels": labels, "counts": counts}


def preferences_by_language(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_language_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        # Get base queryset from homepage events
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_language_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_language_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    language_counts = (
        preferences_language_queryset.values("language__translated_name")
        .annotate(
            translated_name=Case(
                When(language__translated_name="burma", then=Value("burmese")),
                When(language__translated_name="unknown language [qc]", then=Value("mandarin")),
                When(language__translated_name="unknown language [hq]", then=Value("indonesian")),
                When(language__translated_name="unknown language [qm]", then=Value("malay")),
                When(language__translated_name="unknown language [qf]", then=Value("filipino")),
                default=F("language__translated_name"),
                output_field=CharField(),
            )
        )
        .values("translated_name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    labels = []
    counts = []

    for destination in language_counts:
        translated_name = destination["translated_name"]
        if translated_name is None:
            labels.append("Others")
        else:
            labels.append(translated_name.title())

        counts.append(destination["total"])

    return {"labels": labels, "counts": counts}


def preferences_by_organisation(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_organisation_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_organisation_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_organisation_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    organisation_counts = (
        preferences_organisation_queryset.values("org_info__name")
        .annotate(count=Count("org_info__name"))
        .order_by("-count")
    )

    labels = [
        format_org_name_from_display(organisation["org_info__name"]).title()
        for organisation in organisation_counts
    ]

    counts = [organisation["count"] for organisation in organisation_counts]

    return {"labels": labels, "counts": counts}


def get_all_organisations_list(by_field="name"):
    orgs_queryset = Organisation.objects.all()
    return [getattr(org, by_field) for org in orgs_queryset]


def preference_stats_for_export(filters):
    preferences_per_origin_country_responses = preferences_by_origin(**filters)
    preferences_per_destination_country_responses = preferences_by_destination(**filters)
    preferences_by_age_responses = preferences_by_age(**filters)
    preferences_by_gender_responses = preferences_by_gender(**filters)
    preferences_by_language_responses = preferences_by_language(**filters)
    preferences_by_organisation_responses = preferences_by_organisation(**filters)

    return {
        "preferences_by_age": preferences_by_age_responses,
        "preferences_by_gender": preferences_by_gender_responses,
        "preferences_per_origin_country": preferences_per_origin_country_responses,
        "preferences_per_destination_country": preferences_per_destination_country_responses,
        "preferences_selected_user_language": preferences_by_language_responses,
        "work_code_usage": preferences_by_organisation_responses,
    }


def get_cumulative_monthly_new_users(**filters):
    queryset = Preference.objects.all()
    filtered_queryset = preference_filtered_queryset_for_new_user_data(queryset=queryset, **filters)

    data = (
        filtered_queryset.annotate(month=TruncMonth("api_created_at"))
        .values("month")
        .annotate(new_users=Count("id"))
        .order_by("month")
    )

    labels = [entry["month"].strftime("%b, %Y") for entry in data]
    values = [entry["new_users"] for entry in data]

    cummulative_counts = [sum(values[: i + 1]) for i in range(len(values))]

    return {"labels": labels, "counts": values, "cummulative_counts": cummulative_counts}


def get_users_by_country_state(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_count_by_state_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_count_by_state_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_count_by_state_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    preferences_count_by_state = (
        preferences_count_by_state_queryset.values("destination_state__name")
        .annotate(users_count=Count("id"))
        .order_by("destination_state__name")
    )

    # Create separate lists for labels and counts
    labels = [entry["destination_state__name"].title() for entry in preferences_count_by_state]
    counts = [entry["users_count"] for entry in preferences_count_by_state]

    return {
        "labels": labels,
        "counts": counts,
    }


def get_preferences_by_sectors(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_sectors_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_sectors_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_sectors_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    result = (
        preferences_sectors_queryset.filter(sectors_of_work__original_sector_of_work__isnull=False)
        .annotate(
            sector_value=Case(
                When(sectors_of_work__original_sector_of_work__value="Driving", then=Value("Transport")),
                default=F("sectors_of_work__original_sector_of_work__value"),
                output_field=CharField(),
            )
        )
        .values("sector_value")
        .annotate(preferences_count=Count("id"))
        .order_by("-preferences_count")
    )

    SECTOR_MAPPING = {"Agriculture": "Agriculture - Other", "Any": "All"}

    labels = [SECTOR_MAPPING.get(entry["sector_value"], entry["sector_value"]) for entry in result]
    counts = [entry["preferences_count"] for entry in result]

    return {"labels": labels, "counts": counts}


def get_user_counts_by_origin_destination(**filters):
    """
    Retrieves user counts grouped by origin and destination countries.

    This function filters the Preference queryset based on provided filters,
    excludes entries with null origin or destination, and aggregates user counts
    for each origin-destination pair.

    Args:
        **filters: Keyword arguments for filtering the queryset.

    Returns:
        list: A list of dictionaries containing origin, destination, and user count data.
        Each dictionary has the following structure:
        {
            "origin": str,  # Name of the origin country
            "destination": str,  # Name of the destination country
            "count": int  # Number of users for this origin-destination pair
        }
    """
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

        show_new_user_data = filters.get('show_new_user_data', False)
        base_queryset = Preference.objects.all()
        preferences_user_counts_queryset = preference_filtered_queryset_for_new_user_data(
            queryset=base_queryset, 
            **filters
        )
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_user_counts_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_user_counts_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    user_counts = (
        preferences_user_counts_queryset.exclude(origin__isnull=True, destination__isnull=True)
        .values("origin__name", "destination__name")
        .annotate(user_count=Count("id"))
    )

    heatmap_data = [
        {
            "origin": entry["origin__name"],
            "destination": entry["destination__name"],
            "count": entry["user_count"],
        }
        for entry in user_counts
    ]

    return heatmap_data


def get_user_counts_by_geolocation(**filters):
    """
    Retrieves counts of unique users grouped by country from the UserLocation model.
    
    If start_date and end_date are provided in filters, the function filters records to only those 
    with an event_date within the given range. Otherwise, it returns data for all records.
    
    Args:
        **filters: Dictionary containing optional start_date and end_date filters
    
    Returns:
        list: A list of dictionaries, each containing:
        {
            "country": str,         # Name of the country
            "user_count": int,      # Number of unique users for the country
            "created_at": datetime, # Earliest creation time for the country data
            "event_date": datetime  # Earliest event_date for the country data
        }
    """
    
    queryset = UserLocation.objects.all()
    
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    if start_date is None:
        start_date = APPLICATION_POSSIBLE_START_DATE
    if end_date is None:
        end_date = datetime.now().date()
    queryset = queryset.filter(event_date__range=(start_date, end_date))
    
    user_counts = (
        queryset.exclude(country__isnull=True)
        .values("country__name")
        .annotate(
            user_count=Count('user_pseudo_id', distinct=True),
        )
        .order_by("-user_count")
    )

    heatmap_data = [
        {
            "country": entry["country__name"],
            "count": entry["user_count"]       
        }
        for entry in user_counts
    ]
   
    return heatmap_data


def get_sws_workcodes_with_access_code(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_access_code_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_access_code_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    whens = [
        When(organisation_access_code__code=key, then=Value(value))
        for key, value in ACCESS_CODE_MAPPING.items()
    ]

    queryset_data = (
        preferences_access_code_queryset.values(
            organisation_name=F("organisation__name"), access_code=F("organisation_access_code__code")
        )
        .exclude(organisation__name__in=["not specified"])
        .annotate(
            access_code_count=Count("organisation_access_code"),
            mapped_access_code=Case(
                *whens, default=F("organisation_access_code__code"), output_field=CharField()
            ),
        )
        .filter(organisation_access_code__isnull=False)
    )

    return list(queryset_data)


def get_returning_users_grouped_by_original_device_id():
    preferences_with_length = Preference.objects.annotate(
        device_id_length=Length("device_id")
    ).select_related(
        "location_of_potential_work",
        "gender",
        "age",
        "language",
        "origin",
        "destination",
        "api_destination",
        "destination_state",
        "route",
        "organisation_sector",
        "organisation_access_code",
        "factory_farm",
        "organisation",
    )

    original_device_id_annotation = Case(
        When(
            device_id__startswith="jgw-vanilla-", device_id_length__gte=49, then=Substr("device_id", 13, 36)
        ),
        When(device_id__startswith="jgw-vanilla-", then=Substr("device_id", 13, 16)),
        When(device_id__startswith="jgw-", device_id_length__gte=41, then=Substr("device_id", 5, 36)),
        When(device_id__startswith="jgw-", then=Substr("device_id", 5, 16)),
        default=F("device_id"),
        output_field=CharField(),
    )

    preferences_with_original_id = preferences_with_length.annotate(
        original_device_id=original_device_id_annotation
    )

    grouped_preferences_query = (
        preferences_with_original_id.values("original_device_id")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
        .order_by("original_device_id")
    )

    related_preferences = preferences_with_original_id.filter(
        original_device_id__in=[item["original_device_id"] for item in grouped_preferences_query]
    ).values(
        "original_device_id",
        "id",
        "data_source_id",
        "device_id",
        "locale",
        "app_id",
        "cleaned",
        "api_created_at",
        "api_updated_at",
        "location_of_potential_work__name",
        "gender__translated_name",
        "age__range",
        "language__name",
        "origin__name",
        "destination__name",
        "api_destination__name",
        "destination_state__name",
        "route__name",
        "organisation_sector__name",
        "organisation_access_code__code",
        "factory_farm__name",
        "organisation__name",
    )
    grouped_preferences = {}
    for pref in related_preferences:
        original_device_id = pref["original_device_id"]
        if original_device_id not in grouped_preferences:
            grouped_preferences[original_device_id] = []
        grouped_preferences[original_device_id].append(pref)

    for original_device_id, preferences in grouped_preferences.items():
        for pref in preferences:
            pref["api_created_at"] = pref["api_created_at"].strftime("%Y-%m-%d %H:%M:%S")
            pref["api_updated_at"] = pref["api_updated_at"].strftime("%Y-%m-%d %H:%M:%S")
    return grouped_preferences


def extract_preference_for_export(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )
    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_user_counts_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_user_counts_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    
    preferences_user_counts_queryset = preferences_user_counts_queryset.select_related(
        'location_of_potential_work',
        'gender',
        'age', 
        'language',
        'origin',
        'destination',
        'route',
        'organisation_access_code',
        'factory_farm',
        'org_info'
    ).prefetch_related('sectors_of_work')

    # Convert QuerySet to list using values() to get all fields in one query
    preferences_data = preferences_user_counts_queryset.values(
        'data_source_id',
        'device_id',
        'locale',
        'app_id',
        'api_created_at',
        'api_updated_at',
        'location_of_potential_work__name',
        'gender__translated_name',
        'age__range',
        'language__name', 
        'origin__name',
        'destination__name',
        'route__name',
        'organisation_access_code__code',
        'factory_farm__name',
        'org_info__name'
    ).annotate(
        sectors_of_work__translated_name=F('sectors_of_work__translated_name')
    )

    # Group sectors_of_work by preference
    grouped_data = defaultdict(list)
    for pref in preferences_data:
        pref_id = (
            pref['data_source_id'],
            pref['device_id'],
            pref['locale'],
            pref['app_id']
        )
        if pref['sectors_of_work__translated_name']:
            grouped_data[pref_id].append(pref['sectors_of_work__translated_name'])

    # Create final data structure
    final_data = []
    seen_prefs = set()
    for pref in preferences_data:
        pref_id = (
            pref['data_source_id'],
            pref['device_id'], 
            pref['locale'],
            pref['app_id']
        )
        
        if pref_id not in seen_prefs:
            pref_copy = pref.copy()
            pref_copy['sectors_of_work__translated_name'] = grouped_data[pref_id]
            final_data.append(pref_copy)
            seen_prefs.add(pref_id)

    return final_data


def preferences_by_immigration_status(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if show_new_user_data is False:
        base_queryset = get_preferences_by_homepage_events(
            start_date=start_date,
            end_date=end_date
        )

    else:
        base_queryset = Preference.objects.all()

    if show_new_user_data is False:
        preferences_immigration_status_queryset = preference_filtered_queryset_for_active_users_data(
            queryset=base_queryset, 
            **filters
        )
    else:
        preferences_immigration_status_queryset = preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)

    results = (
        preferences_immigration_status_queryset.values("immigration_status__name")
        .annotate(
            name=Case(
                When(immigration_status__name__isnull=True, then=Value("Not Specified")),
                default="immigration_status__name",
                output_field=CharField(),
            )
        )
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    return {
        "labels": [item["name"] for item in results],
        "counts": [item["count"] for item in results],
    }


def get_preferences_by_device_id(device_id):
    preferences = PreferenceHistory.objects.filter(device_id__icontains=device_id).select_related(
        'gender',
        'age',
        'language',
        'origin',
        'destination',
        'api_destination',
        'destination_state',
        'route',
        'organisation_sector',
        'organisation_access_code',
        'factory_farm',
        'organisation',
    ).order_by('-api_created_at')
    return preferences


def get_preferences_by_homepage_events(start_date=None, end_date=None):
    if start_date is None:
        start_date = APPLICATION_POSSIBLE_START_DATE
    if end_date is None:
        end_date = datetime.now().date()

    homepage_events = BigqueryHomepageEventData.objects.filter(
        Q(event_date__range=(start_date, end_date))
    )
        
    device_ids = homepage_events.values_list('device_id', flat=True).distinct()


    preferences = Preference.objects.filter(
        device_id__in=device_ids
    )

    return preferences
