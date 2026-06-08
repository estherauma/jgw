"""
Populate UniqueInlineQuestion and UniqueMessagingQuestion from lead response tables.

Usage:
    python manage.py sync_unique_lead_questions
"""

from django.core.management.base import BaseCommand

from question.unique_question_sync import (
    sync_unique_inline_questions,
    sync_unique_messaging_questions,
)


class Command(BaseCommand):
    help = "Sync unique inline and messaging question catalogs from lead responses."

    def handle(self, *args, **options):
        inline_created, inline_updated = sync_unique_inline_questions()
        messaging_created, messaging_updated = sync_unique_messaging_questions()
        self.stdout.write(
            self.style.SUCCESS(
                "Unique inline questions: "
                f"{inline_created} created, {inline_updated} updated. "
                "Unique messaging questions: "
                f"{messaging_created} created, {messaging_updated} updated."
            )
        )
