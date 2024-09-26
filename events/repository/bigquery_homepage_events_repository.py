from django.db.models import Count, Q
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
    ).aggregate(  # Ensure device_id is not null
        total_unique_device_count=Count("device_id", distinct=True)
    )[
        "total_unique_device_count"
    ]

    return format_thousands_with_commas(total_active_user_count)


def get_monthly_active_user_count(**filters):
    queryset = BigqueryHomepageEventData.objects.all()

    filtered_queryset = filter_bigquery_homepage_event_data(queryset, **filters)

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
