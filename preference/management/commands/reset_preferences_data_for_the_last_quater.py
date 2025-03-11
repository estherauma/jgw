from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from preference.models import Preference


class Command(BaseCommand):
    help = 'Deletes preference instances from the last 3 months'

    @transaction.atomic
    def handle(self, *args, **options):
        three_months_ago = datetime.now() - timedelta(days=90)

        deleted_count = Preference.objects.filter(
            created_at__gte=three_months_ago
        ).delete()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_count} preferences from the last 3 months'
            )
        )
