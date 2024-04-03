from django.core.management.base import BaseCommand
from preference.logic.attach_sectors_to_preferences_logic import (
    attach_sectors_to_preferences,
    clean_sectors_of_work,
    # export_sectors_of_work_to_excel,
    stringified_sectors_of_work_to_list,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        attach_sectors_to_preferences()
        stringified_sectors_of_work_to_list()
        clean_sectors_of_work()
        self.stdout.write(
            self.style.SUCCESS("Successfully attached sectors to preferences and cleaned sectors of work")
        )
