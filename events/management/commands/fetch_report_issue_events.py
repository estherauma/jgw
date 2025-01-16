from django.core.management.base import BaseCommand
from events.logic.add_report_issue_events import fetch_report_issue_events_from_api_to_db
from pipeline.models import CommandLog


class Command(BaseCommand):
    help = "Fetches and stores report issue submitted events from BigQuery"

    def handle(self, *args, **options):
        try:
            fetch_report_issue_events_from_api_to_db()
            CommandLog.objects.create(
                command_name="fetch_report_issue_events",
                data_fetch="Report Issue Events",
                error="None",
                command_status=True,
            )
            self.stdout.write(self.style.SUCCESS("Successfully fetched and stored report issue events"))
        except Exception as e:
            CommandLog.objects.create(
                command_name="fetch_report_issue_events",
                data_fetch="Report Issue Events",
                error=str(e),
                command_status=False,
            )
            self.stdout.write(self.style.ERROR(f"Failed to fetch report issue events: {str(e)}"))
