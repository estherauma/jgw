
from datetime import timedelta, date
from django.core.management.base import BaseCommand

from common.reports import get_inlineQNs_responses_report

class Command(BaseCommand):
     def handle(self, *args, **options):
        # 1st feb to 31 mar
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        start = "2022-06-1"
        end = "2023-03-31"
        get_inlineQNs_responses_report(start=start, end=end)