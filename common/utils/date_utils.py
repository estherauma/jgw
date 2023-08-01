from datetime import datetime, timedelta
from django.utils import timezone as django_timezone

def previous_dates(days: int = 1) -> str:
    return (datetime.today() - timedelta(days)).strftime("%Y-%m-%d")


def get_desired_time(minutes):
    current_time = datetime.now()
    desired_time = current_time + timedelta(minutes=minutes)
    return desired_time


def todays_date():
    return datetime.today().strftime("%Y-%m-%d")

def date_to_string(date):
    return date.strftime("%Y-%m-%d")


def django_date_make_aware(date):
    return django_timezone.make_aware(date)

def string_to_date(date, format = "%Y-%m-%d"):
    return datetime.strptime(date, format)