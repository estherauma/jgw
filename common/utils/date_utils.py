from datetime import datetime, timedelta, time, timezone
from django.utils import timezone as django_timezone
from dateutil import parser

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

def parse_api_date(date_string):
    """
    Parse a date string from an API and return a datetime object with timezone info.
    
    Args:
        date_string (str): The date string in ISO format.

    Returns:
        datetime.datetime: A datetime object with timezone information.
    """
    date_time_obj = parser.isoparse(date_string)
    return date_time_obj


def date_to_datetime(date_obj):
    """
    Converts a date object to a datetime object with timezone information set to UTC.

    Parameters:
        date_obj (datetime.date): The date object to be converted.

    Returns:
        datetime.datetime: A datetime object representing the input date with UTC timezone.

    Example:
        >>> import datetime
        >>> from datetime import timezone
        >>> date = datetime.date(2023, 9, 15)
        >>> result = date_to_datetime(date)
        >>> print(result)
        2023-09-15 00:00:00+00:00

    Note:
        The resulting datetime object will have a time of midnight (00:00:00) and the
        timezone set to UTC.
    """
    tz = timezone.utc
    dt = datetime.combine(date_obj, time.min).replace(tzinfo=tz)
    
    return dt