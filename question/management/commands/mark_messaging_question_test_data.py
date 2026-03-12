from django.core.management.base import BaseCommand

from question.logic.mark_messaging_question_test_data import mark_messaging_question_standard_test_data


class Command(BaseCommand):
    help = "Mark MessagingQuestionStandard rows as test data when question_id is in the test question ID list."

    def handle(self, *args, **kwargs):
        self.stdout.write("Marking messaging question standard test data...")
        updated_count = mark_messaging_question_standard_test_data()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully marked {updated_count} messaging question standard(s) as test data.")
        )
