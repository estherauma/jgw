from django.core.management.base import BaseCommand

from preference.logic.update_sector_of_work_data import fetch_preferences_data_from_api


class Command(BaseCommand):
    help = 'Update the sectors of work information from Oct 2023 to Feb 2024'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Updating sector of work...'))

        fetch_preferences_data_from_api()

        self.stdout.write(self.style.SUCCESS('Successfully updated sectors of work'))
