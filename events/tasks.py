from celery import shared_task
from events.management.commands.cache_bigquery_data import add_biquery_data

@shared_task(name="cache_bigquery_data")
def cache_bigquery_data():
    add_biquery_data()