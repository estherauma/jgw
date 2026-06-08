from django.core.management.base import BaseCommand
from pipeline.models import CommandLog
from common.services.api_client import JustGoodWorkAPIClient

from question.logic.add_inline_question_logic import store_new_v3_inline_questions
from question.unique_question_sync import sync_unique_inline_questions

class Command(BaseCommand):
    help = 'Fetches inline questions v3 from API and stores them in the new chain structure (Lead, Followup, FollowupFollowup)'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting to fetch inline questions v3 from API...')
            
            jgw_api_client = JustGoodWorkAPIClient()
            sync_unique_inline_questions()
            created_count = store_new_v3_inline_questions(jgw_api_client)

            
            if created_count > 0:
                CommandLog.objects.create(
                    command_name='add_inline_question_v3_from_api',
                    data_fetch='Inline questions v3',
                    error='None',
                    command_status=True
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully fetched and stored {created_count} inline questions v3 from API'))
            else:
                CommandLog.objects.create(
                    command_name='add_inline_question_v3_from_api',
                    data_fetch='Inline questions v3',
                    error='No new data to store',
                    command_status=False
                )
                self.stdout.write(self.style.WARNING('No new inline questions v3 to store (empty list from API)'))
            
        except Exception as e:
            CommandLog.objects.create(
                command_name='add_inline_question_v3_from_api',
                data_fetch='Inline questions v3',
                error=str(e),
                command_status=False
            )
            
            self.stdout.write(self.style.ERROR(f'Error fetching inline questions v3 from API: {e}'))
            raise

