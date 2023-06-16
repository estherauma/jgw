from django.core.management.base import BaseCommand
from common.app_events import AppEvents
from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData


def add_biquery_data(select_all=False):
    appEvents = AppEvents()
    bigquery_data = appEvents.bigquery_data(select_all=select_all)
    
    bigquery_chapters_data = bigquery_data['bigquery_chapters_data']
    bigquery_firstopen_homepage_data = bigquery_data['bigquery_firstopen_homepage_data']
    
    # Process BigQueryChaptersData
    for item in bigquery_chapters_data:
        BigQueryChaptersData.objects.get_or_create(
            event_date='2023-06-17',
            chapters='chapters',
            users=item['users'],
            count=item['count']
        )

    # Process BigQueryFirstOpenHomepageData
    for item in bigquery_firstopen_homepage_data:
        BigQueryFirstOpenHomepageData.objects.get_or_create(
            event_date='2023-06-17',
            users=item['users'],
            count=item['count'],
            event_name='event_name'
        )

    
class Command(BaseCommand):
    def handle(self, *args, **options):
        add_biquery_data()
