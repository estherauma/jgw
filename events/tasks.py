from celery import shared_task
from common.app_events import AppEvents

@shared_task(name="fetch_app_events_data")
def fetch_app_events_data():
    pass