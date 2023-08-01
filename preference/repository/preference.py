


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

    age_counts = preferences_age_queryset.values('age__range').annotate(total=Count('id'))

    labels = [age['age__range'] for age in age_counts]
    counts = [age['total'] for age in age_counts]

    return {
        "labels": labels,
        "counts": counts
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

    labels = [gender['gender__translated_name'] for gender in gender_counts]
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

    labels = [origin['origin__name'] for origin in origin_counts]
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

    labels = [destination['destination__name'] for destination in destination_counts]
    counts = [destination['total'] for destination in destination_counts]

    return {
        "labels": labels,
        "counts": counts
    }