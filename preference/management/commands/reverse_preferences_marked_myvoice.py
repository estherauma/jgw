from django.core.management.base import BaseCommand

from preference.logic.add_preferences_logic import reverse_myvoice_preferences


class Command(BaseCommand):
    help = 'Reverse preferences marked as myvoice'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Reversing preferences marked as myvoice...'))
        reverse_myvoice_preferences()
        self.stdout.write(self.style.SUCCESS('Successfully reversed preferences marked as myvoice.'))
