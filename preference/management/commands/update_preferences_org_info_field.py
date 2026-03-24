from django.core.management.base import BaseCommand

from preference.logic.update_perference_organisation_info import (
    update_preferences_org_info_from_organisation,
)
from preference.models import Preference


class Command(BaseCommand):
    help = 'Update preferences with organisation info based on organisation codes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Set org_info to null and is_missing_organisation_info_cleaned to True for all preferences',
        )

    def handle(self, *args, **options):
        try:
            if options['reset']:
                self.stdout.write('Resetting org_info and is_missing_organisation_info_cleaned...')
                updated_count = Preference.objects.update(
                    org_info=None,
                    is_missing_organisation_info_cleaned=False,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Reset org_info for {updated_count} preferences'
                    )
                )
                return

            self.stdout.write(self.style.SUCCESS('Starting to update preferences with organisation info...'))

            updated_count = update_preferences_org_info_from_organisation()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} preferences with organisation info'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating preferences with organisation info: {str(e)}')
            )