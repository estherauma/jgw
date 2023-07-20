from datetime import datetime, timedelta

def previous_dates(days: int = 1) -> str:
    return (datetime.today() - timedelta(days)).strftime("%Y-%m-%d")


def get_desired_time(minutes):
    current_time = datetime.now()
    desired_time = current_time + timedelta(minutes=minutes)
    return desired_time


def todays_date():
    return datetime.today().strftime("%Y-%m-%d")