from django.core.management.base import BaseCommand

from question.logic.add_inline_question_logic import reverse_myvoice_inline_questions


class Command(BaseCommand):
    help = 'Reverse inline questions marked as myvoice'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Reversing inline questions marked as myvoice...'))
        reverse_myvoice_inline_questions()
        self.stdout.write(self.style.SUCCESS('Successfully reversed inline questions marked as myvoice.'))
