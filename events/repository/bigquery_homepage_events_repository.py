from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.dateformat import DateFormat
from common.utils.strings import format_thousands_with_commas
from events.filters import filter_bigquery_homepage_event_data
from events.models import BigqueryHomepageEventData


def get_total_active_user_within_period(**filters):
    queryset = BigqueryHomepageEventData.objects.all()

    filtered_queryset = filter_bigquery_homepage_event_data(queryset, **filters)
    total_active_user_count = filtered_queryset.filter(
        device_id__isnull=False
    ).aggregate(  
        total_unique_device_count=Count("device_id", distinct=True)
    )[
        "total_unique_device_count"
    ]

    return format_thousands_with_commas(total_active_user_count)


def get_monthly_active_user_count(current_user, **filters):
    queryset = BigqueryHomepageEventData.objects.all()

    filtered_queryset = filter_bigquery_homepage_event_data(queryset, current_user, **filters)

    monthly_counts = (
        filtered_queryset.filter(device_id__isnull=False)
        .annotate(month=TruncMonth("event_date"))
        .values("month")
        .annotate(unique_device_count=Count("device_id", distinct=True))
        .order_by("month")
    )

    active_user_count = [
        {"month": DateFormat(entry["month"]).format("M, Y"), "count": entry["unique_device_count"]}
        for entry in monthly_counts
    ]

    return active_user_count


def get_user_counts_by_geo_country(**filters):
    """
    Retrieves user counts grouped by geo_country.

    This function filters the BigqueryHomepageEventData queryset based on provided filters,
    excludes entries with null geo_country, and aggregates user counts for each country.

    Args:
        **filters: Keyword arguments for filtering the queryset.

    Returns:
        list: A list of dictionaries containing country and user count data.
        Each dictionary has the following structure:
        {
            "country": str,  # Name of the country
            "count": int  # Number of users from this country
        }
    """
    queryset = BigqueryHomepageEventData.objects.all()
    filtered_queryset = filter_bigquery_homepage_event_data(queryset, **filters)
    
    user_counts = (
        filtered_queryset.exclude(geo_country__isnull=True)
        .values("geo_country__name")
        .annotate(user_count=Count("device_id", distinct=True))
        .order_by("-user_count")
    )

    geo_data = [
        {
            "country": entry["geo_country__name"],
            "count": entry["user_count"],
        }
        for entry in user_counts
    ]

    return geo_data
