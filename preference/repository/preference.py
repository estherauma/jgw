


from common.helpers.preference_helpers.organisation import format_org_name_fro_display
from core.filters import generic_filtered_queryset
from preference.models import Preference


def preferences_count(
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
):
    
    queryset = Preference.objects.all()
    
    preferences_count_queryset = generic_filtered_queryset(
        queryset = queryset, 
        start_date = start_date, 
        end_date = end_date,
        origin_countries = origin_countries,
        destination_countries = destination_countries,
    )
        
    return preferences_count_queryset.count()

from django.db.models import Count

def preferences_by_age(
    start_date=None, 
    end_date=None, 
    origin_countries=None, 
    destination_countries=None
):
    
    preferences_age_queryset = generic_filtered_queryset(
        queryset=Preference.objects.all(),
        start_date=start_date,
        end_date=end_date,
        origin_countries=origin_countries,
        destination_countries=destination_countries,
    )

    age_counts = preferences_age_queryset.values('age__translated_range').annotate(total=Count('id'))
    labels = [age['age__translated_range'].upper() for age in age_counts]
    counts = [age['total'] for age in age_counts]
    
    group_mapping = {
        "60+": ["60+", "60+"],
        "51-60": ["51-60"],
        "41-50": ["41-50"],
        "31-40": ["31-35", "36-40", "31-40", "36 - 40"],
        "21-30": ["21-25", "21-30"],
        "18-20": ["15-18", "15-20", "18-20", "19-20"],
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
            if label == "PREFER NOT TO ANSWER":
                combined_values["PREFER NOT TO ANSWER"] += value
    final_labels = []
    final_counts = []
    for group, value in combined_values.items():
        final_labels.append(group)
        final_counts.append(value)

    return {
        "labels": final_labels,
        "counts": final_counts
    }


def preferences_by_gender(
    start_date=None, 
    end_date=None, 
    origin_countries=None, 
    destination_countries=None
):
    preferences_gender_queryset = generic_filtered_queryset(
        queryset=Preference.objects.all(),
        start_date=start_date,
        end_date=end_date,
        origin_countries=origin_countries,
        destination_countries=destination_countries,
    )

    gender_counts = preferences_gender_queryset.values('gender__translated_name').annotate(total=Count('id'))

    labels = [gender['gender__translated_name'].upper() for gender in gender_counts]
    counts = [gender['total'] for gender in gender_counts]

    return {
        "labels": labels,
        "counts": counts
    }
    

def preferences_by_origin(
    start_date=None, 
    end_date=None, 
    origin_countries=None, 
    destination_countries=None
):
    preferences_origin_queryset = generic_filtered_queryset(
        queryset=Preference.objects.all(),
        start_date=start_date,
        end_date=end_date,
        origin_countries=origin_countries,
        destination_countries=destination_countries,
    )

    origin_counts = preferences_origin_queryset.values('origin__name').annotate(total=Count('id'))

    labels = [origin['origin__name'].upper() for origin in origin_counts if origin['origin__name'] is not None]
    counts = [origin['total'] for origin in origin_counts]

    return {
        "labels": labels,
        "counts": counts
    }

def preferences_by_destination(
    start_date=None, 
    end_date=None, 
    origin_countries=None, 
    destination_countries=None
):
    preferences_destination_queryset = generic_filtered_queryset(
        queryset=Preference.objects.all(),
        start_date=start_date,
        end_date=end_date,
        origin_countries=origin_countries,
        destination_countries=destination_countries,
    )

    destination_counts = preferences_destination_queryset.values('destination__name').annotate(total=Count('id'))

    labels = [destination['destination__name'].upper() for destination in destination_counts]
    counts = [destination['total'] for destination in destination_counts]

    return {
        "labels": labels,
        "counts": counts
    }
    
    
def preferences_by_language(
    start_date=None, 
    end_date=None, 
    origin_countries=None, 
    destination_countries=None
):
    preferences_language_queryset = generic_filtered_queryset(
        queryset=Preference.objects.all(),
        start_date=start_date,
        end_date=end_date,
        origin_countries=origin_countries,
        destination_countries=destination_countries,
    )

    language_counts = preferences_language_queryset.values('language__translated_name').annotate(total=Count('id'))

    labels = [destination['language__translated_name'].upper() for destination in language_counts]
    counts = [destination['total'] for destination in language_counts]

    return {
        "labels": labels,
        "counts": counts
    }
    
    
def preferences_by_organisation(
    start_date=None, 
    end_date=None, 
    origin_countries=None, 
    destination_countries=None
):
    organisation = generic_filtered_queryset(
        queryset=Preference.objects.all(),
        start_date=start_date,
        end_date=end_date,
        origin_countries=origin_countries,
        destination_countries=destination_countries,
    )

    organisation_counts = organisation.values('organisation__name').annotate(total=Count('id'))

    labels = [format_org_name_fro_display(organisation['organisation__name']).upper() for organisation in organisation_counts]
    counts = [organisation['total'] for organisation in organisation_counts]

    return {
        "labels": labels,
        "counts": counts
    }