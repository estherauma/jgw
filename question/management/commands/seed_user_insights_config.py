"""
Seed User Insights report and indicator configuration (matches current UI mock).

Usage:
    python manage.py seed_user_insights_config
    python manage.py seed_user_insights_config --clear
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from question.user_insights_models import (
    UserInsightsIndicator,
    UserInsightsIndicatorInlineQuestion,
    UserInsightsIndicatorMessagingQuestion,
    UserInsightsReport,
)


REPORTS = [
    {
        "slug": "early_risk",
        "title": "Early Risk Report",
        "description": (
            "The Early Risk Report shows data from worker responses "
            "to help identify potential risks."
        ),
        "hint": "Click on a graph to see more details.",
        "pdf_label": "Download PDF of questions",
        "breakdown_header": "Indicators:",
        "display_order": 1,
    },
    {
        "slug": "decent_employment",
        "title": "Decent Employment Report",
        "description": (
            "The Decent Employment Report shows data from worker responses "
            "related to job quality and working conditions."
        ),
        "hint": "Click on a graph to see more details.",
        "pdf_label": "Download PDF of questions",
        "breakdown_header": "Decent employment indicators:",
        "display_order": 2,
    },
    {
        "slug": "responsible_recruitment",
        "title": "Responsible Recruitment Report",
        "description": (
            "The Responsible Recruitment Report shows data from worker responses "
            "about recruitment practices and transparency."
        ),
        "hint": "Click on a graph to see more details.",
        "pdf_label": "Download PDF of categories",
        "breakdown_header": "Responsible Recruitment Indicators:",
        "display_order": 3,
    },
]

# Indicators per report slug: matches preference/views.py mock breakdown + donut mapping.
INDICATORS_BY_REPORT = {
    "early_risk": [
        {
            "slug": "abuse_vulnerability",
            "name": "Abuse of vulnerability",
            "color": "#e67e22",
            "breakdown_index": 0,
            "show_on_donut": True,
            "donut_slot": 0,
            "display_order": 1,
        },
        {
            "slug": "deception",
            "name": "Deception",
            "color": "#1abc9c",
            "breakdown_index": 1,
            "show_on_donut": True,
            "donut_slot": 2,
            "display_order": 2,
        },
        {
            "slug": "restriction_movement",
            "name": "Restriction of movement",
            "color": "#f1c40f",
            "breakdown_index": 2,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 3,
        },
        {
            "slug": "isolation",
            "name": "Isolation",
            "color": "#3498db",
            "breakdown_index": 3,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 4,
        },
        {
            "slug": "physical_sexual_violence",
            "name": "Physical and sexual violence",
            "color": "#e74c3c",
            "breakdown_index": 4,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 5,
        },
        {
            "slug": "intimidation_threats",
            "name": "Intimidation and threats",
            "color": "#9b59b6",
            "breakdown_index": 5,
            "show_on_donut": True,
            "donut_slot": 4,
            "display_order": 6,
        },
        {
            "slug": "retention_identity",
            "name": "Retention of identity documents",
            "color": "#e91e63",
            "breakdown_index": 6,
            "show_on_donut": True,
            "donut_slot": 3,
            "display_order": 7,
        },
        {
            "slug": "withholding_wages",
            "name": "Withholding of wages",
            "color": "#00bcd4",
            "breakdown_index": 7,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 8,
        },
        {
            "slug": "debt_bondage",
            "name": "Debt bondage",
            "color": "#795548",
            "breakdown_index": 8,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 9,
        },
        {
            "slug": "abusive_conditions",
            "name": "Abusive working and living conditions",
            "color": "#607d8b",
            "breakdown_index": 9,
            "show_on_donut": True,
            "donut_slot": 1,
            "display_order": 10,
        },
        {
            "slug": "excessive_overtime",
            "name": "Excessive overtime",
            "color": "#ff5722",
            "breakdown_index": 10,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 11,
        },
    ],
    "decent_employment": [
        {
            "slug": "decent_work",
            "name": "Decent work",
            "color": "#2980b9",
            "breakdown_index": 0,
            "show_on_donut": True,
            "donut_slot": 0,
            "display_order": 1,
        },
        {
            "slug": "equal_treatment",
            "name": "Equal treatment",
            "color": "#8e44ad",
            "breakdown_index": 1,
            "show_on_donut": True,
            "donut_slot": 1,
            "display_order": 2,
        },
        {
            "slug": "safe_workplace",
            "name": "Safe workplace",
            "color": "#16a085",
            "breakdown_index": 2,
            "show_on_donut": True,
            "donut_slot": 2,
            "display_order": 3,
        },
        {
            "slug": "social_protection",
            "name": "Social protection",
            "color": "#d35400",
            "breakdown_index": 3,
            "show_on_donut": True,
            "donut_slot": 3,
            "display_order": 4,
        },
        {
            "slug": "dialogue_at_work",
            "name": "Dialogue at work",
            "color": "#c0392b",
            "breakdown_index": 4,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 5,
        },
        {
            "slug": "career_development",
            "name": "Career development",
            "color": "#27ae60",
            "breakdown_index": 5,
            "show_on_donut": True,
            "donut_slot": 4,
            "display_order": 6,
        },
    ],
    "responsible_recruitment": [
        {
            "slug": "accommodation",
            "name": "Accommodation",
            "color": "#e67e22",
            "breakdown_index": 0,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 1,
        },
        {
            "slug": "fair_treatment",
            "name": "Fair Treatment",
            "color": "#2ecc71",
            "breakdown_index": 1,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 2,
        },
        {
            "slug": "onboarding",
            "name": "Onboarding",
            "color": "#3498db",
            "breakdown_index": 2,
            "show_on_donut": True,
            "donut_slot": 1,
            "display_order": 3,
        },
        {
            "slug": "addressing_issues",
            "name": "Addressing Issues",
            "color": "#9b59b6",
            "breakdown_index": 3,
            "show_on_donut": True,
            "donut_slot": 3,
            "display_order": 4,
        },
        {
            "slug": "changing_job",
            "name": "Changing Job",
            "color": "#e74c3c",
            "breakdown_index": 4,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 5,
        },
        {
            "slug": "recruitment",
            "name": "Recruitment",
            "color": "#1abc9c",
            "breakdown_index": 5,
            "show_on_donut": True,
            "donut_slot": 0,
            "display_order": 6,
        },
        {
            "slug": "travel",
            "name": "Travel",
            "color": "#f39c12",
            "breakdown_index": 6,
            "show_on_donut": False,
            "donut_slot": None,
            "display_order": 7,
        },
        {
            "slug": "employment",
            "name": "Employment",
            "color": "#34495e",
            "breakdown_index": 7,
            "show_on_donut": True,
            "donut_slot": 2,
            "display_order": 8,
        },
    ],
}


class Command(BaseCommand):
    help = "Seed User Insights reports and indicators (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all User Insights config before seeding.",
        )

    def _ensure_tables_exist(self):
        table_names = set(connection.introspection.table_names())
        if "question_userinsightsreport" not in table_names:
            raise CommandError(
                "User Insights tables are missing. Apply migrations first:\n"
                "  python manage.py migrate question"
            )

    @transaction.atomic
    def handle(self, *args, **options):
        self._ensure_tables_exist()

        if options["clear"]:
            deleted_inline, _ = UserInsightsIndicatorInlineQuestion.objects.all().delete()
            deleted_messaging, _ = UserInsightsIndicatorMessagingQuestion.objects.all().delete()
            deleted_indicators, _ = UserInsightsIndicator.objects.all().delete()
            deleted_reports, _ = UserInsightsReport.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    "Cleared User Insights config: "
                    f"{deleted_reports} reports, {deleted_indicators} indicators, "
                    f"{deleted_inline} inline questions, {deleted_messaging} messaging questions."
                )
            )

        report_count = 0
        indicator_count = 0

        for report_data in REPORTS:
            slug = report_data["slug"]
            fields = {k: v for k, v in report_data.items() if k != "slug"}
            fields["is_active"] = True
            report, created = UserInsightsReport.objects.update_or_create(
                slug=slug,
                defaults=fields,
            )
            report_count += 1
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} report: {report.slug}")

            for indicator_data in INDICATORS_BY_REPORT.get(slug, []):
                indicator_slug = indicator_data["slug"]
                indicator_fields = {
                    k: v
                    for k, v in indicator_data.items()
                    if k != "slug"
                }
                indicator_fields["is_active"] = True
                indicator, ind_created = UserInsightsIndicator.objects.update_or_create(
                    report=report,
                    slug=indicator_slug,
                    defaults=indicator_fields,
                )
                indicator_count += 1
                ind_action = "Created" if ind_created else "Updated"
                donut = (
                    f"donut slot {indicator.donut_slot}"
                    if indicator.show_on_donut
                    else "breakdown only"
                )
                self.stdout.write(
                    f"    {ind_action} indicator: {indicator.slug} "
                    f"(breakdown_index={indicator.breakdown_index}, {donut})"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {report_count} reports, {indicator_count} indicators seeded."
            )
        )
        self.stdout.write(
            "Run `python manage.py sync_unique_lead_questions`, then link indicator "
            "questions in admin (Unique inline / messaging question dropdowns)."
        )
