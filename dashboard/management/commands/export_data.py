
from datetime import timedelta, date
from django.core.management.base import BaseCommand

from common.reports import get_inlineQNs_responses_report

class Command(BaseCommand):
     def handle(self, *args, **options):
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        get_inlineQNs_responses_report(start=thirty_days_ago, end=today)