from django.core.management.base import BaseCommand

from help_contacts.logic.add_help_contacts_logic import fetch_help_contacts_from_api_to_db

# django command class
class Command(BaseCommand):
    help = 'Fetch help contacts from api and add to db'

    def handle(self, *args, **options):
        fetch_help_contacts_from_api_to_db()
        self.stdout.write(self.style.SUCCESS('Successfully fetched help contacts from api and added to db'))