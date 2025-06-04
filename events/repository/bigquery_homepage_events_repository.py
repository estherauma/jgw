from datetime import datetime
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.dateformat import DateFormat
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, PUBLIC_USER_DATA_START_DATE
from common.utils.preferences import get_date_13_months_ago
from common.utils.strings import format_thousands_with_commas
from events.filters import filter_bigquery_homepage_event_data
from events.models import BigqueryHomepageEventData
from preference.filters import preference_filtered_queryset_for_active_users_data
from preference.models import Preference
from users.utils import get_user_start_date


def get_total_active_user_within_period(**filters):
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()
    user_start_date = get_user_start_date(filters.get('current_user'))
    start_date = filters.get('start_date') or user_start_date
    end_date = filters.get('end_date')
    if not start_date:
        start_date = get_date_13_months_ago()
    if not end_date:
        end_date = datetime.now().date()
    
    total_active_user = Preference.objects.filter(
        bigqueryhomepageeventdata__event_date__range=(start_date, end_date)
    ).values_list('device_id', flat=True).distinct()

    total_active_user = Preference.objects.filter(
        device_id__in=total_active_user
    )
    total_active_user_count = preference_filtered_queryset_for_active_users_data(
            queryset=total_active_user, 
            **filters
        )
    unique_device_count = total_active_user_count.values('device_id').distinct().count()
    
    return format_thousands_with_commas(unique_device_count)


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
    if isinstance(filters.get('current_user'), type) or str(filters.get('current_user')) == "AnonymousUser":
        filters['start_date'] = PUBLIC_USER_DATA_START_DATE
        filters['end_date'] = datetime.now().date()

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
