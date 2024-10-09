from django.core.management.base import BaseCommand

from events.logic.add_homepage_events_to_db import reverse_myvoice_bigquery_homepage_events



class Command(BaseCommand):
    help = 'Reverse myvoice marked homepage events'
    def handle(self, *args, **options):
        reverse_myvoice_bigquery_homepage_events()
        self.stdout.write(self.style.SUCCESS('Successfully reversed myvoice marked homepage events.'))