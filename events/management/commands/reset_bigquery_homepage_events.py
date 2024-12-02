from django.core.management.base import BaseCommand

from events.models import (
    BigqueryHomepageEventData,
)


class Command(BaseCommand):
    """Deletes everything in the imported Bigquery Homepage Events tables

    Args:
        BaseCommand (BaseCommand): Django commands base class

    Returns: None
    """

    def handle(self, *args, **options):
        BigqueryHomepageEventData.objects.all().delete()
