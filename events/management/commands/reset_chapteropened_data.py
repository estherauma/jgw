from django.core.management.base import BaseCommand

from events.models import (
    ChaptersOpened,
)


class Command(BaseCommand):
    """Deletes everything in the chapters opened tables

    Args:
        BaseCommand (BaseCommand): Django commands base class
        
    Returns: None
    """
    def handle(self, *args, **options):
        ChaptersOpened.objects.all().delete()

      
