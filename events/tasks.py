from celery import shared_task
from events.management.commands.cache_bigquery_data import add_biquery_data
from events.models import OneTimeEventJob

@shared_task(name="cache_bigquery_data")
def cache_bigquery_data():
    add_biquery_data()
    

@shared_task(name="load_all_bigquery_data_at_once")
def load_all_bigquery_data_at_once():
    load_all_bigquery_data_at_once, created = OneTimeEventJob.objects.get_or_create(name="load_all_bigquery_data_at_once")
    
    if not load_all_bigquery_data_at_once.run:
        add_biquery_data(select_all=True)
        load_all_bigquery_data_at_once.run = True
        load_all_bigquery_data_at_once.save()