from django.core.management.base import BaseCommand

from events.models import (
    Chapter,
    ImmigrationStatusChapterTitle,
)


class Command(BaseCommand):
    """Deletes everything in the chapters title tables

    Args:
        BaseCommand (BaseCommand): Django commands base class
        
    Returns: None
    """
    def handle(self, *args, **options):
        Chapter.objects.all().delete()
        ImmigrationStatusChapterTitle.objects.all().delete()
       