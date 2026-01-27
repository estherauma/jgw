from django.core.management.base import BaseCommand
from pipeline.models import CommandLog
from common.services.api_client import MessagingAPIClient

from question.logic.add_messaging_question_logic import store_new_v2_messaging_questions


class Command(BaseCommand):
    help = 'Fetches messaging questions v2 from API and stores them in the new chain structure (Lead, Followup, FollowupFollowup)'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting to fetch messaging questions v2 from API...')
            
            jgw_api_client = MessagingAPIClient()
            
            created_count = store_new_v2_messaging_questions(jgw_api_client) or 0
            
            if created_count > 0:
                CommandLog.objects.create(
                    command_name='add_messaging_question_v2_from_api',
                    data_fetch='Messaging questions v2',
                    error='None',
                    command_status=True
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully stored messaging questions v2 from API. created={created_count}'
                    )
                )
            else:
                CommandLog.objects.create(
                    command_name='add_messaging_question_v2_from_api',
                    data_fetch='Messaging questions v2',
                    error='No new records (empty list from API)',
                    command_status=True
                )
                self.stdout.write(
                    self.style.WARNING('No new messaging questions v2 to store (empty list from API)')
                )
            
        except Exception as e:
            CommandLog.objects.create(
                command_name='add_messaging_question_v2_from_api',
                data_fetch='Messaging questions v2',
                error=str(e),
                command_status=False
            )
            
            self.stdout.write(self.style.ERROR(f'Error fetching messaging questions v2 from API: {e}'))
            raise

