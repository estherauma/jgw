from django.core.management.base import BaseCommand

from preference.logic.update_original_sector_of_work_translation import (
    reset_is_original_sector_of_work_in_english_in_the_sector_of_work_table,
)


class Command(BaseCommand):
    help = "Reset is_original_sector_of_work_in_english column in Sector of Work table to default (False)"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Resetting is_original_sector_of_work_in_english column..."))

        reset_is_original_sector_of_work_in_english_in_the_sector_of_work_table()

        self.stdout.write(
            self.style.SUCCESS("Successfully reset is_original_sector_of_work_in_english column.")
        )
