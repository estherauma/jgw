from django.core.management.base import BaseCommand
from pipeline.models import CommandLog
from preference.logic.add_original_sectors_of_work_to_db import process_and_store_original_work_sectors


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            process_and_store_original_work_sectors()

            self.stdout.write(
                self.style.SUCCESS("Successfully fetched orignal work sector from api and added to db")
            )
        except Exception as e:

            self.stdout.write(self.style.ERROR(f"Error fetching work sectors from api: {e}"))
