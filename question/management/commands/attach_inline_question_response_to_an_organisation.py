from django.core.management.base import BaseCommand

from question.logic.attached_question_to_organisation_response import update_organisation_inline_question




class Command(BaseCommand):
    def handle(self, *args, **options):
        update_organisation_inline_question()
        self.stdout.write(self.style.SUCCESS('Successfully attached response to myvoice and evergreen organisation'))
