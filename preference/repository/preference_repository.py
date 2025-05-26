from collections import defaultdict
from datetime import datetime
from django.db.models import Case, When, Value, CharField, F, Count
from django.db.models.functions import Cast, Substr, Length
from django.db.models import Q
from django.db.models.functions import TruncMonth
from common.const.value_const import ACCESS_CODE_MAPPING, APPLICATION_POSSIBLE_START_DATE, PUBLIC_USER_DATA_START_DATE
from common.helpers.preference_helpers.gender import normalize_gender_name

from common.helpers.preference_helpers.organisation import format_org_name_from_display
from common.utils.preferences import get_date_13_months_ago
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
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_age_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields and do grouping in the database
    age_counts = (
        preferences_age_queryset
        .values('age__translated_range')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Define age group mapping
    group_mapping = {
        "60+": ["60+"],
        "51-60": ["51-60"],
        "41-50": ["41-50", "40+"],
        "31-40": ["31-35", "36-40", "31-40", "36 - 40", "31 - 35"],
        "21-30": ["21-25", "21-30", "26-30", "21 - 25"],
        "18-20": ["15-18", "15-20", "18-20", "19-20", "15 - 20"],
        "15-17": ["15-17"],
    }

    # Initialize combined values with all groups
    combined_values = {group: 0 for group in group_mapping}
    combined_values["PREFER NOT TO ANSWER"] = 0

    # Process age counts in a single pass
    for age in age_counts:
        age_range = age['age__translated_range'].title() if age['age__translated_range'] else None
        if not age_range:
            continue

        if age_range in ["PREFER NOT TO ANSWER", "PREFERNOTTOANSWER"]:
            combined_values["PREFER NOT TO ANSWER"] += age['total']
            continue

        for group, ranges in group_mapping.items():
            if age_range in ranges:
                combined_values[group] += age['total']
                break

    # Convert to final format
    return {
        "labels": list(combined_values.keys()),
        "counts": list(combined_values.values())
    }


def preferences_by_gender(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_gender_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields and do grouping in the database
    gender_counts = (
        preferences_gender_queryset
        .values('gender__translated_name')
        .annotate(
            normalized_name=Case(
                When(
                    gender__translated_name__isnull=True,
                    then=Value('Not Specified')
                ),
                default=F('gender__translated_name'),
                output_field=CharField(),
            )
        )
        .values('normalized_name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Process gender counts in a single pass
    label_sums = defaultdict(int)
    for gender in gender_counts:
        normalized_label = normalize_gender_name(gender['normalized_name']).title()
        label_sums[normalized_label] += gender['total']

    return {
        "labels": list(label_sums.keys()),
        "counts": list(label_sums.values())
    }


def preferences_by_origin(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_origin_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields
    origin_counts = (
        preferences_origin_queryset
        .values('origin__name')
        .annotate(
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
        .values('normalized_origin')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Convert to lists directly from the queryset
    return {
        "labels": [origin["normalized_origin"].title() for origin in origin_counts if origin["normalized_origin"]],
        "counts": [origin["total"] for origin in origin_counts if origin["normalized_origin"]]
    }


def preferences_by_destination(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_destination_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields and do grouping in the database
    destination_counts = (
        preferences_destination_queryset
        .values('destination__name')
        .annotate(
            normalized_name=Case(
                When(
                    destination__name__isnull=True,
                    then=Value('Not Specified')
                ),
                default=F('destination__name'),
                output_field=CharField(),
            )
        )
        .values('normalized_name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Process results in a single pass
    return {
        "labels": [dest['normalized_name'].title() for dest in destination_counts if dest['normalized_name']],
        "counts": [dest['total'] for dest in destination_counts if dest['normalized_name']]
    }


def preferences_by_language(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_language_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields and do grouping in the database
    language_counts = (
        preferences_language_queryset
        .values('language__translated_name')
        .annotate(
            translated_name=Case(
                When(language__translated_name="burma", then=Value("burmese")),
                When(language__translated_name="unknown language [qc]", then=Value("mandarin")),
                When(language__translated_name="unknown language [hq]", then=Value("indonesian")),
                When(language__translated_name="unknown language [qm]", then=Value("malay")),
                When(language__translated_name="unknown language [qf]", then=Value("filipino")),
                When(language__translated_name__isnull=True, then=Value("Others")),
                default=F('language__translated_name'),
                output_field=CharField(),
            )
        )
        .values('translated_name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Process results in a single pass
    return {
        "labels": [lang['translated_name'].title() for lang in language_counts],
        "counts": [lang['total'] for lang in language_counts]
    }


def preferences_by_organisation(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['show_new_user_data'] = True
        filters['start_date'] = get_date_13_months_ago()
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
    if start_date is None:
        start_date = get_date_13_months_ago()
    if end_date is None:
        end_date = datetime.now().date()

    if show_new_user_data is False:
        base_queryset = Preference.objects.filter(
            bigqueryhomepageeventdata__event_date__range=(start_date, end_date)
        ).distinct()

        # Convert to Preference queryset
        base_queryset = Preference.objects.filter(id__in=base_queryset)

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
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_count_by_state_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields and do grouping in the database
    preferences_count_by_state = (
        preferences_count_by_state_queryset
        .values('destination_state__name')
        .annotate(
            normalized_name=Case(
                When(
                    destination_state__name__isnull=True,
                    then=Value('Not Specified')
                ),
                default=F('destination_state__name'),
                output_field=CharField(),
            )
        )
        .values('normalized_name')
        .annotate(users_count=Count('id'))
        .order_by('normalized_name')
    )

    # Process results in a single pass
    return {
        "labels": [state['normalized_name'].title() for state in preferences_count_by_state if state['normalized_name']],
        "counts": [state['users_count'] for state in preferences_count_by_state if state['normalized_name']]
    }


def get_preferences_by_sectors(**filters):
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_sectors_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Define sector mapping at the module level for better performance
    SECTOR_MAPPING = {
        "Agriculture": "Agriculture - Other",
        "Any": "All",
        "Driving": "Transport"
    }

    # Use values() to only fetch needed fields and do grouping in the database
    result = (
        preferences_sectors_queryset
        .filter(sectors_of_work__original_sector_of_work__isnull=False)
        .annotate(
            sector_value=Case(
                *[
                    When(
                        sectors_of_work__original_sector_of_work__value=key,
                        then=Value(value)
                    ) for key, value in SECTOR_MAPPING.items()
                ],
                default=F("sectors_of_work__original_sector_of_work__value"),
                output_field=CharField(),
            )
        )
        .values('sector_value')
        .annotate(preferences_count=Count('id'))
        .order_by('-preferences_count')
    )

    # Process results in a single pass
    return {
        "labels": [entry['sector_value'] for entry in result],
        "counts": [entry['preferences_count'] for entry in result]
    }


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
    show_new_user_data = filters.get('show_new_user_data', False)
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_user_counts_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields and do grouping in the database
    user_counts = (
        preferences_user_counts_queryset
        .exclude(origin__isnull=True, destination__isnull=True)
        .values('origin__name', 'destination__name')
        .annotate(
            user_count=Count('id'),
            normalized_origin=Case(
                When(origin__name__isnull=True, then=Value('Not Specified')),
                default=F('origin__name'),
                output_field=CharField(),
            ),
            normalized_destination=Case(
                When(destination__name__isnull=True, then=Value('Not Specified')),
                default=F('destination__name'),
                output_field=CharField(),
            )
        )
        .values('normalized_origin', 'normalized_destination', 'user_count')
        .order_by('-user_count')
    )

    # Process results in a single pass
    return [
        {
            "origin": entry['normalized_origin'],
            "destination": entry['normalized_destination'],
            "count": entry['user_count'],
        }
        for entry in user_counts
    ]


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
        start_date = get_date_13_months_ago()
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
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_access_code_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields and do grouping in the database
    queryset_data = (
        preferences_access_code_queryset
        .values(
            organisation_name=F('org_info__name'),
            access_code=F('organisation_access_code__code')
        )
        .exclude(org_info__name__in=["Organisation Not Specified"])
        .annotate(
            access_code_count=Count('organisation_access_code'),
            mapped_access_code=Case(
                *[
                    When(
                        organisation_access_code__code=key,
                        then=Value(value)
                    ) for key, value in ACCESS_CODE_MAPPING.items()
                ],
                default=F('organisation_access_code__code'),
                output_field=CharField(),
            )
        )
        .filter(organisation_access_code__isnull=False)
        .order_by('-access_code_count')
    )

    # Return list directly from queryset
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
        base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
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
    start_date = filters.get('start_date') or get_date_13_months_ago()
    end_date = filters.get('end_date') or datetime.now().date()

    # Get base queryset with optimized querying
    base_queryset = get_base_queryset(show_new_user_data, start_date, end_date)
    
    # Apply filters
    preferences_immigration_status_queryset = (
        preference_filtered_queryset_for_active_users_data(queryset=base_queryset, **filters)
        if not show_new_user_data
        else preference_filtered_queryset_for_new_user_data(queryset=base_queryset, **filters)
    )

    # Use values() to only fetch needed fields and do grouping in the database
    results = (
        preferences_immigration_status_queryset
        .values('immigration_status__name')
        .annotate(
            name=Case(
                When(immigration_status__name__isnull=True, then=Value("Not Specified")),
                default=F('immigration_status__name'),
                output_field=CharField(),
            )
        )
        .values('name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Process results in a single pass
    return {
        "labels": [item['name'] for item in results],
        "counts": [item['count'] for item in results]
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

def get_base_queryset(show_new_user_data, start_date, end_date):
    """Centralized function to get base queryset with optimized querying"""
    if show_new_user_data is False:
        preferences = Preference.objects.filter(
            bigqueryhomepageeventdata__event_date__range=(start_date, end_date)
        ).select_related(
            'origin',
            'destination',
            'gender',
            'age',
            'language',
            'immigration_status',
            'org_info'
        ).distinct()

        return Preference.objects.filter(id__in=preferences)
    return Preference.objects.all()
