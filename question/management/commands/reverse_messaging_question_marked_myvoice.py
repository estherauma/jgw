from django.core.management.base import BaseCommand

from question.logic.add_messaging_question_logic import reverse_myvoice_messaging_questions


class Command(BaseCommand):
    help = 'Reverse messaging questions marked as myvoice'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Reversing messaging questions marked as myvoice...'))
        reverse_myvoice_messaging_questions()
        self.stdout.write(self.style.SUCCESS('Successfully reversed messaging questions marked as myvoice.'))
