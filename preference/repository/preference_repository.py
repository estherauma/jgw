from collections import defaultdict
from django.db.models import Case, When, Value, CharField, F, Count
from common.helpers.preference_helpers.gender import normalize_gender_name

from common.helpers.preference_helpers.organisation import format_org_name_from_display
from preference.filters import preference_filtered_queryset
from preference.models import Organisation, Preference
from users.utils import get_user_organisations


def preferences_count(**filters):
    queryset = Preference.objects.all()

    preferences_count_queryset = preference_filtered_queryset(queryset=queryset, **filters)

    return preferences_count_queryset.count()


def preferences_by_age(**filters):
    preferences_age_queryset = preference_filtered_queryset(queryset=Preference.objects.all(), **filters)

    age_counts = (
        preferences_age_queryset.values("age__translated_range")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    labels = [age["age__translated_range"].upper() for age in age_counts]
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
    combined_values["PREFER NOT TO ANSWER"] = 0
    for label, value in zip(labels, counts):
        for group, label_list in group_mapping.items():
            if label in label_list:
                combined_values[group] += value
                break
        else:
            if label == "PREFER NOT TO ANSWER" or label == "PREFERNOTTOANSWER":
                combined_values["PREFER NOT TO ANSWER"] += value
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
        normalized_label = normalize_gender_name(gender["gender__translated_name"]).upper()
        label_sums[normalized_label] += gender["total"]

    summed_labels = list(label_sums.keys())
    summed_counts = list(label_sums.values())

    return {"labels": summed_labels, "counts": summed_counts}


def preferences_by_origin(**filters):
    preferences_origin_queryset = preference_filtered_queryset(queryset=Preference.objects.all(), **filters)

    origin_counts = (
        preferences_origin_queryset.values("origin__name").annotate(total=Count("id")).order_by("-total")
    )

    labels = [
        origin["origin__name"].upper() for origin in origin_counts if origin["origin__name"] is not None
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

    labels = [destination["destination__name"].upper() for destination in destination_counts]
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

    #     "burma": "burmese",
    # "": "mandarin",
    # "": "indonesian",
    # "": "malay",
    # "unknown language [qf]": "filipino",

    labels = [destination["translated_name"].upper() for destination in language_counts]
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
        format_org_name_from_display(organisation["organisation_name"]).upper()
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
