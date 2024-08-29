from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils.dateformat import DateFormat
from events.filters import filter_bigquery_homepage_event_data
from events.models import BigqueryHomepageEventData


def get_monthly_active_user_count(**filters):
    queryset = BigqueryHomepageEventData.objects.all()

    filtered_queryset = filter_bigquery_homepage_event_data(queryset, **filters)

    monthly_counts = (
        filtered_queryset
        .filter(device_id__isnull=False) 
        .annotate(month=TruncMonth('event_date')) 
        .values('month') 
        .annotate(unique_device_count=Count('device_id', distinct=True)) 
        .order_by('month') 
    )

    active_user_count = [
        {
            "month": DateFormat(entry['month']).format('M, Y'),
            "count": entry['unique_device_count']
        }
        for entry in monthly_counts
    ]

    return active_user_count