from django.core.management.base import BaseCommand
from events.logic.add_homepage_events_to_db import fetch_and_save_homepage_events_to_db



class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_and_save_homepage_events_to_db()
