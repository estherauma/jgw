from django.core.management.base import BaseCommand

from events.models import (
    LinksClickEvent
)


class Command(BaseCommand):
    """Deletes everything in the imported Link Clicks Events tables

    Args:
        BaseCommand (BaseCommand): Django commands base class
        
    Returns: None
    """
    def handle(self, *args, **options):
        LinksClickEvent.objects.all().delete()
       