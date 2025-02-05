from django.core.management.base import BaseCommand
from events.logic.add_user_engagement_location_to_db import fetch_and_save_user_engagement_location_to_db
from pipeline.models import CommandLog


class Command(BaseCommand):
    help = "Fetches and stores user engagement location data from BigQuery"

    def handle(self, *args, **options):
        try:
            fetch_and_save_user_engagement_location_to_db()
            CommandLog.objects.create(
                command_name="add_user_engagement_location",
                data_fetch="User Engagement Location",
                error="None",
                command_status=True,
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully fetched and stored user engagement location data")
            )
        except Exception as e:
            CommandLog.objects.create(
                command_name="add_user_engagement_location",
                data_fetch="User Engagement Location",
                error=str(e),
                command_status=False,
            )
            self.stdout.write(
                self.style.ERROR(f"Failed to fetch user engagement location data: {str(e)}")
            ) 