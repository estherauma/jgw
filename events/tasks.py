from celery import shared_task
from events.management.commands.cache_bigquery_data import add_biquery_data
from events.models import OneTimeEventJob

@shared_task(name="cache_bigquery_data")
def cache_bigquery_data():
    add_biquery_data()
    

@shared_task(name="load_bigquery_data_once")
def load_bigquery_data_once():
    load_bigquery_event_data, created = OneTimeEventJob.objects.get_or_create(name="load_bigquery_data_once")
    
    if not load_bigquery_event_data.run:
        add_biquery_data(select_all=True)
        load_bigquery_event_data.run = True
        load_bigquery_event_data.save()