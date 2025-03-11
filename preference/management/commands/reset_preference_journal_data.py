from django.core.management.base import BaseCommand
from preference.models import PreferenceHistory

class Command(BaseCommand):
    help = "Reset preference journal data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Resetting preference journal data..."))

        PreferenceHistory.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS("Successfully reset preference journal data.")
        )
