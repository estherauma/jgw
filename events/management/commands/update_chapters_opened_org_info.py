from django.core.management.base import BaseCommand

from events.logic.update_events_data_with_org_info import (
    update_chapters_opened_org_info_from_organisation,
)
from events.models import ChaptersOpened


class Command(BaseCommand):
    help = (
        'Reset is_org_info_cleaned on ChaptersOpened and re-resolve org_info '
        'via update_chapters_opened_org_info_from_organisation'
    )

    def handle(self, *args, **options):
        try:
            self.stdout.write('Resetting is_org_info_cleaned on ChaptersOpened...')
            reset_count = ChaptersOpened.objects.filter(
                is_org_info_cleaned=True,
            ).update(is_org_info_cleaned=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Reset is_org_info_cleaned for {reset_count} chapters opened'
                )
            )

            self.stdout.write('Updating chapters opened org_info...')
            updated_count = update_chapters_opened_org_info_from_organisation()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated org_info for {updated_count} chapters opened'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error updating chapters opened org_info: {str(e)}'
                )
            )
