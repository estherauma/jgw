from django.core.management.base import BaseCommand

from events.logic.add_chapters_opened_data import reverse_myvoice_chapters_opened_events


class Command(BaseCommand):
    help = 'Reverse myvoice marked chapters opened events'
    def handle(self, *args, **options):
        reverse_myvoice_chapters_opened_events()
        self.stdout.write(self.style.SUCCESS('Successfully reversed myvoice marked chapters opened events.'))