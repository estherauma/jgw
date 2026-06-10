"""
Rebuild LeadMessagingQuestionResponse.question_indicators from User Insights config.

Usage:
    python manage.py sync_lead_messaging_question_indicators
"""

from django.core.management.base import BaseCommand

from question.user_insights_helpers import rebuild_lead_messaging_question_indicators


class Command(BaseCommand):
    help = (
        "Clear question_indicators on all lead messaging responses, then assign "
        "indicators from UserInsightsIndicatorMessagingQuestion by question_key."
    )

    def handle(self, *args, **options):
        stats = rebuild_lead_messaging_question_indicators()
        self.stdout.write(
            self.style.SUCCESS(
                "Lead messaging question_indicators rebuilt: "
                f"{stats['cleared']} cleared, "
                f"{stats['relations_created']} links created on "
                f"{stats['linked_leads']} lead responses "
                f"({stats['skipped_leads']} leads had no matching indicator config, "
                f"{stats['configured_keys']} question keys configured)."
            )
        )
