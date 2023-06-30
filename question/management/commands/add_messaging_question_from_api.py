from django.core.management.base import BaseCommand

from question.logic.add_messaging_question_logic import fetch_messaging_questions_from_api_to_db




class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_messaging_questions_from_api_to_db()
        self.stdout.write(self.style.SUCCESS('Successfully added messaging questions from API to DB'))
