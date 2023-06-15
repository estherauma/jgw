from django.core.management.base import BaseCommand
from common.app_events import AppEvents
from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData


def add_biquery_data():
    appEvents = AppEvents()
    bigquery_data = appEvents.bigquery_data()
    
    bigquery_chapters_data = bigquery_data['bigquery_chapters_data']
    bigquery_firstopen_homepage_data = bigquery_data['bigquery_firstopen_homepage_data']

    # Bulk insert for BigQueryChaptersData
    chapters_data_objects = [
        BigQueryChaptersData(
            event_date=item['event_date'],
            chapters=item['chapters'],
            users=item['users'],
            count=item['count']
        )
        for item in bigquery_chapters_data
    ]
    BigQueryChaptersData.objects.bulk_create(chapters_data_objects)

    # Bulk insert for BigQueryFirstOpenHomepageData
    homepage_data_objects = [
        BigQueryFirstOpenHomepageData(
            event_date=item['event_date'],
            users=item['users'],
            count=item['count'],
            event_name=item['event_name']
        )
        for item in bigquery_firstopen_homepage_data
    ]
    BigQueryFirstOpenHomepageData.objects.bulk_create(homepage_data_objects)

    
class Command(BaseCommand):
    def handle(self, *args, **options):
        add_biquery_data()
