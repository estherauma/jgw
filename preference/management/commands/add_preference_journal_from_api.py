from django.core.management.base import BaseCommand
from pipeline.models import CommandLog

from preference.logic.add_preferences_journal import fetch_preferences_journal_from_api_to_db



class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            fetch_preferences_journal_from_api_to_db()
            CommandLog.objects.create(command_name='add_preferences_journal_from_api',data_fetch='Preferences',error='None',command_status=True)
            self.stdout.write(self.style.SUCCESS('Successfully fetched preferences journal from api and added to db'))
        except Exception as e:
            CommandLog.objects.create(command_name='add_preferences_journal_from_api',data_fetch='Preferences',error=e, command_status=False)
            self.stdout.write(self.style.ERROR(f'Error fetching preferences journal from api: {e}'))
