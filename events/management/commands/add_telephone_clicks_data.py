from django.core.management.base import BaseCommand

from events.logic.add_telephone_click import fetch_telephone_click_events_from_api_to_db


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_telephone_click_events_from_api_to_db()
