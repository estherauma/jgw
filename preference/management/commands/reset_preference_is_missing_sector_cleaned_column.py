from django.core.management.base import BaseCommand

from preference.logic import reset_is_missing_sector_cleaned


class Command(BaseCommand):
    help = 'Reset is_missing_sector_cleaned column in Preference table to default (False)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Resetting is_missing_sector_cleaned column...'))

        reset_is_missing_sector_cleaned.reset_is_missing_sector_cleaned_in_the_preference_table()

        self.stdout.write(self.style.SUCCESS('Successfully reset is_missing_sector_cleaned column.'))
