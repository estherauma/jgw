from django.core.management.base import BaseCommand

from events.logic.add_chapters_feedback_data import reverse_myvoice_chapters_feedback



class Command(BaseCommand):
    help = 'Reverse myvoice marked chapters feedback'
    def handle(self, *args, **options):
        reverse_myvoice_chapters_feedback()
        self.stdout.write(self.style.SUCCESS('Successfully reversed myvoice marked chapters feedback.'))