from django.core.management.base import BaseCommand

from events.models import (
    UserLocation, 
) 


class Command(BaseCommand):
    """Deletes everything in the imported events tables

    Args:
        BaseCommand (BaseCommand): Django commands base class
        
    Returns: None
    """
    def handle(self, *args, **options):

        
        UserLocation.objects.all().delete()
