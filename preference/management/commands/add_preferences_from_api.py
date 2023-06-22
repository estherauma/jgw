from django.core.management.base import BaseCommand

from preference.logic.add_preferences_logic import fetch_preferences_from_api_to_db



class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_preferences_from_api_to_db()
        self.stdout.write(self.style.SUCCESS('Successfully fetched preferences from api and added to db'))
