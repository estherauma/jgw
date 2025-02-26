from django.core.management.base import BaseCommand
from preference.logic.update_perference_organisation_info import update_bigquery_homepage_event_org_info_from_organisation, update_preferences_org_info_from_organisation
from question.logic.update_question_data_with_org_info import update_inline_question_org_info_from_organisation

class Command(BaseCommand):
    help = 'Update preferences with organisation info based on organisation codes'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.SUCCESS('Starting to update preferences with organisation info...'))
            
            updated_count = update_inline_question_org_info_from_organisation()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} preferences with organisation info'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating preferences with organisation info: {str(e)}')
            )