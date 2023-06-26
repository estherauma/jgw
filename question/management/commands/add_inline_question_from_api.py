from django.core.management.base import BaseCommand

from question.logic.add_inline_question_logic import fetch_inline_questions_from_api_to_db




class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_inline_questions_from_api_to_db()
        self.stdout.write(self.style.SUCCESS('Successfully fetched inline questions from api and added to db'))
