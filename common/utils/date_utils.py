from datetime import datetime, timedelta

def previous_dates(days: int = 1) -> str:
    return (datetime.today() - timedelta(days)).strftime("%Y-%m-%d")