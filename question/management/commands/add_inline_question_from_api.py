from django.core.management.base import BaseCommand
from pipeline.models import CommandLog

from question.logic.add_inline_question_logic import fetch_inline_questions_from_api_to_db




class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            fetch_inline_questions_from_api_to_db()
            CommandLog.objects.create(command_name='add_inline_question_from_api',data_fetch='Inline questions',error='None',command_status=True)
            self.stdout.write(self.style.SUCCESS('Successfully fetched inline questions from api and added to db'))
        except Exception as e:
            CommandLog.objects.create(command_name='add_inline_question_from_api', command_status=False,error=e, data_fetch='Inline questions')
            self.stdout.write(self.style.ERROR(f'Error fetching inline questions from api: {e}'))
