from collections import defaultdict
from django.db.models import Case, When, Value, CharField, F, Count
from django.db.models.functions import Cast,Substr,Length
from django.db.models import Q
from django.db.models.functions import TruncMonth
from common.const.value_const import ACCESS_CODE_MAPPING
from common.helpers.preference_helpers.gender import normalize_gender_name

from common.helpers.preference_helpers.organisation import format_org_name_from_display
from common.utils.strings import format_thousands_with_commas
from preference.filters import preference_filtered_queryset
from preference.models import Organisation, Preference, SectorsOfWorkMapper


def preferences_count(**filters):
    queryset = Preference.objects.all()

    preferences_count_queryset = preference_filtered_queryset(queryset=queryset, **filters)

    return format_thousands_with_commas(preferences_count_queryset.count())


def preferences_by_age(**filters):
    preferences_age_queryset = preference_filtered_queryset(queryset=Preference.objects.all(), **filters)

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
    preferences_gender_queryset = preference_filtered_queryset(queryset=Preference.objects.all(), **filters)

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
    preferences_origin_queryset = preference_filtered_queryset(queryset=Preference.objects.all(), **filters)

    preferences_origin_queryset = preferences_origin_queryset.annotate(
        normalized_origin=Case(
            When(origin__name__iexact='phillippines', then=Value('Philippines')),
            When(origin__name__iexact='philippines', then=Value('Philippines')),
            default=F('origin__name'),
            output_field=CharField(),
        )
    )

    origin_counts = (
        preferences_origin_queryset.values("normalized_origin")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    labels = [
        origin["normalized_origin"].title() for origin in origin_counts if origin["normalized_origin"] is not None
    ]
    counts = [origin["total"] for origin in origin_counts]

    return {"labels": labels, "counts": counts}


def preferences_by_destination(**filters):
    preferences_destination_queryset = preference_filtered_queryset(
        queryset=Preference.objects.all(), **filters
    )

    destination_counts = (
        preferences_destination_queryset.values("destination__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    labels = [destination["destination__name"].title() for destination in destination_counts]
    counts = [destination["total"] for destination in destination_counts]

    return {"labels": labels, "counts": counts}


def preferences_by_language(**filters):
    preferences_language_queryset = preference_filtered_queryset(queryset=Preference.objects.all(), **filters)

    language_counts = (
        preferences_language_queryset.values("language__translated_name")
        .annotate(
            translated_name=Case(
                When(
                    language__translated_name="burma",
                    then=Value("burmese"),
                ),
                When(
                    language__translated_name="unknown language [qc]",
                    then=Value("mandarin"),
                ),
                When(
                    language__translated_name="unknown language [hq]",
                    then=Value("indonesian"),
                ),
                When(
                    language__translated_name="unknown language [qm]",
                    then=Value("malay"),
                ),
                When(
                    language__translated_name="unknown language [qf]",
                    then=Value("filipino"),
                ),
                default=F("language__translated_name"),
                output_field=CharField(),
            )
        )
        .values("translated_name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    labels = [destination["translated_name"].title() for destination in language_counts]
    counts = [destination["total"] for destination in language_counts]

    return {"labels": labels, "counts": counts}


def preferences_by_organisation(**filters):
    organisation_queryset = preference_filtered_queryset(queryset=Preference.objects.all(), **filters)

    organisation_counts = (
        organisation_queryset.values("organisation__name")
        .annotate(
            organisation_name=Case(
                When(
                    organisation__name__in=["placeuk", "seasonal worker scheme - placeuk"],
                    then=Value("PlaceUk"),
                ),
                When(
                    organisation__name__icontains="hops",
                    then=Value("seasonal worker scheme - hops"),
                ),
                default=F("organisation__name"),
                output_field=CharField(),
            )
        )
        .values("organisation_name")
        .annotate(count=Count("organisation_name"))
        .exclude(organisation__name__in=["not specified", "tst-org"])
        .order_by("-count")
    )

    labels = [
        format_org_name_from_display(organisation["organisation_name"]).title()
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
    filtered_queryset = preference_filtered_queryset(queryset=queryset, **filters)

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
    queryset = Preference.objects.all()
    filtered_queryset = preference_filtered_queryset(queryset=queryset, **filters)
    preferences_count_by_state = (
        filtered_queryset.values("destination_state__name")
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
    queryset = Preference.objects.all()
    filtered_queryset = preference_filtered_queryset(queryset=queryset, **filters)

    sectors_of_work_mapper_instances = SectorsOfWorkMapper.objects.exclude(sectors__is_disabled=True)

    initial_case_list = [
        {
            "then_value": sof.mapper.lower(),
            "match_list": [sec.translated_name for sec in sof.sectors.all()],
        }
        for sof in sectors_of_work_mapper_instances
    ]

    case_list = [initial_case for initial_case in initial_case_list if initial_case["match_list"]]

    when_list = [
        When(sectors_of_work__translated_name__in=case["match_list"], then=Value(case["then_value"]))
        for case in case_list
        if case["match_list"]
    ]

    aggregated_data = (
        filtered_queryset.exclude(sectors_of_work__is_disabled=True)
        .annotate(
            sectors_of_work__translated_name=Case(
                *when_list,
                default=F("sectors_of_work__translated_name"),
                output_field=CharField(),
            ),
        )
        .values("sectors_of_work__translated_name")
        .annotate(count=Count("id"))
    )

    sector_counts = {}

    for entry in aggregated_data:
        sector_name = entry["sectors_of_work__translated_name"]
        count = entry["count"]

        if sector_name in sector_counts:
            sector_counts[sector_name.trim()] += count
        else:
            sector_counts[sector_name] = count

    labels = list(sector_counts.keys())
    count = list(sector_counts.values())

    result_dict = {"labels": [label.capitalize() for label in labels], "counts": count}

    return result_dict


def get_sws_workcodes_with_access_code(**filters):
    queryset = Preference.objects.all()
    filtered_queryset = preference_filtered_queryset(queryset=queryset, **filters)

    whens = [When(organisation_access_code__code=key, then=Value(value)) for key, value in ACCESS_CODE_MAPPING.items()]

    queryset_data = (
        filtered_queryset
        .values(
            organisation_name=F("organisation__name"),
            access_code=F("organisation_access_code__code")
        )
        .exclude(organisation__name__in=["not specified"])
        .annotate(
            access_code_count=Count("organisation_access_code"),
            mapped_access_code=Case(
                *whens,
                default=F("organisation_access_code__code"),
                output_field=CharField()
            )
        )
        .filter(organisation_access_code__isnull=False)
    )

    return list(queryset_data)

def get_returning_users_grouped_by_original_device_id():
    preferences_with_length = Preference.objects.annotate(
        device_id_length=Length('device_id')
    )

    original_device_id_annotation = Case(
        When(device_id__startswith='jgw-vanilla-', device_id_length__gte=49, then=Substr('device_id', 13, 36)),
        When(device_id__startswith='jgw-vanilla-', then=Substr('device_id', 13, 16)),
        When(device_id__startswith='jgw-', device_id_length__gte=41, then=Substr('device_id', 5, 36)),
        When(device_id__startswith='jgw-', then=Substr('device_id', 5, 16)),
        default=F('device_id'),
        output_field=CharField()
    )

    preferences_with_original_id = preferences_with_length.annotate(
        original_device_id=original_device_id_annotation
    )

    grouped_preferences_query = preferences_with_original_id.values('original_device_id').annotate(
        count=Count('id')
    ).filter(count__gt=1).order_by('original_device_id')

    grouped_preferences = {}
    for pref in grouped_preferences_query:
        original_device_id = pref['original_device_id']
        if original_device_id not in grouped_preferences:
            grouped_preferences[original_device_id] = []

        related_preferences = preferences_with_original_id.filter(
            original_device_id=original_device_id
        ).values(
            'id', 'data_source_id', 'device_id', 'locale', 'app_id', 'cleaned', 
            'api_created_at', 'api_updated_at',
            'location_of_potential_work__name', 'gender__translated_name', 'age__range', 
            'language__name', 'origin__name', 'destination__name', 
            'api_destination__name', 'destination_state__name', 'route__name', 
            'organisation_sector__name', 'organisation_access_code__code', 
            'factory_farm__name', 'organisation__name'
        )
        grouped_preferences[original_device_id].extend(related_preferences)

    for original_device_id, preferences in grouped_preferences.items():
        for pref in preferences:
            pref['api_created_at'] = pref['api_created_at'].strftime('%Y-%m-%d %H:%M:%S')
            pref['api_updated_at'] = pref['api_updated_at'].strftime('%Y-%m-%d %H:%M:%S')
    print(len(grouped_preferences))
    return grouped_preferences