from django.core.management.base import BaseCommand
from django.db import transaction

from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.utils.date_utils import previous_dates, todays_date
from common.utils.dictionary_utils import change_dictionary_keys_lowercase
from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData


def add_bigquery_chapters_data():
    
    start_date= APPLICATION_POSSIBLE_START_DATE
    end_date= previous_dates()
    
    latest_query_chapter_data = BigQueryChaptersData.objects.last()
    if latest_query_chapter_data:
        start_date = latest_query_chapter_data.created_at.strftime("%Y-%m-%d")
        
    appEvents = AppEvents()
    
    chapters_data = appEvents.bigquery_chapters_data(
        start_date=start_date,
        end_date=end_date
    )
    
    for cd in chapters_data:
        item = change_dictionary_keys_lowercase(cd)
        
        instance, _ = BigQueryChaptersData.objects.get_or_create(
            event_date=item.get('event_date')
        )
        instance.chapters=item.get('chapters')
        instance.users=item.get('users')
        instance.count=item.get('count')
        instance.save()

def add_bigquery_firstopen_homepage_data():
    
    start_date= APPLICATION_POSSIBLE_START_DATE
    end_date= previous_dates()
    
    latest_firstopen_homepage_data = BigQueryFirstOpenHomepageData.objects.last()
    if latest_firstopen_homepage_data:
        start_date = latest_firstopen_homepage_data.created_at.strftime("%Y-%m-%d")
        
    appEvents = AppEvents()
    
    firstopen_homepage_data = appEvents.bigquery_firstopen_homepage_data(
        start_date=start_date,
        end_date=end_date
    )
    
    for fhd in firstopen_homepage_data:
        item = change_dictionary_keys_lowercase(fhd)

        instance, _ = BigQueryFirstOpenHomepageData.objects.get_or_create(
            event_date=item.get('event_date')
        )
        instance.users=item.get('users')
        instance.count=item.get('count')
        instance.event_name=item.get('event_name')
        instance.save()


@transaction.atomic
def add_biquery_data():
    add_bigquery_chapters_data()
    add_bigquery_firstopen_homepage_data()

    
class Command(BaseCommand):
    def handle(self, *args, **options):
        add_biquery_data()
