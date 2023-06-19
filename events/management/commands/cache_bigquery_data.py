from django.core.management.base import BaseCommand
from common.app_events import AppEvents
from common.utils.dictionary_utils import change_dictionary_keys_lowercase
from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData


def add_biquery_data(select_all=False):
    if select_all:
        BigQueryFirstOpenHomepageData.objects.all().delete()
        BigQueryChaptersData.objects.all().delete()
        
    appEvents = AppEvents()
    bigquery_data = appEvents.bigquery_data(select_all=select_all)
    
    bigquery_chapters_data = bigquery_data['bigquery_chapters_data']
    bigquery_firstopen_homepage_data = bigquery_data['bigquery_firstopen_homepage_data']
    
    # Process BigQueryChaptersData
    for chapter_data in bigquery_chapters_data:
        item = change_dictionary_keys_lowercase(chapter_data)
        # BigQueryChaptersData.objects.get_or_create(
        #     event_date=item.get('event_date'),
        #     chapters=item.get('chapters'),
        #     users=item.get('users'),
        #     count=item.get('count')
        # )

    # Process BigQueryFirstOpenHomepageData
    for firstopen_homepage_data in bigquery_firstopen_homepage_data:
        item = change_dictionary_keys_lowercase(firstopen_homepage_data)
        # BigQueryFirstOpenHomepageData.objects.get_or_create(
        #     event_date=item.get('event_date'),
        #     users=item.get('users'),
        #     count=item.get('count'),
        #     event_name=item.get('event_name')
        # )

    
class Command(BaseCommand):
    def handle(self, *args, **options):
        add_biquery_data()
