from django.core.management.base import BaseCommand
from pipeline.models import CommandLog

from question.logic.add_messaging_question_logic import fetch_messaging_questions_from_api_to_db




class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            fetch_messaging_questions_from_api_to_db()
            CommandLog.objects.create(command_name='add_messaging_question_from_api',data_fetch='Messsaging questions',error='None',command_status=True)
            self.stdout.write(self.style.SUCCESS('Successfully added messaging questions from API to DB'))
        except Exception as e:
            CommandLog.objects.create(command_name='add_messaging_question_from_api',data_fetch='Messaging questions',error=e, command_status=False)
            self.stdout.write(self.style.ERROR(f'Error fetching messaging questions data from api: {e}'))
            
