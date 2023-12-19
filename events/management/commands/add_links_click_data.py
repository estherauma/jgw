from django.core.management.base import BaseCommand

from events.logic.add_links_click_data import fetch_links_click_events_from_api_to_db


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_links_click_events_from_api_to_db()
