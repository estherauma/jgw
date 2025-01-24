from django.core.management.base import BaseCommand
from preference.logic.update_preferences_with_orgcode import update_preferences_org_code_field


class Command(BaseCommand):
    help = 'Update preferences with organisation info based on organisation codes'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.SUCCESS('Starting to update preferences with organisation info...'))
            
            updated_count = update_preferences_org_code_field()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} preferences with organisation info'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating preferences with organisation info: {str(e)}')
            )
