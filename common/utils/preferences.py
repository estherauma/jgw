import re

from django.http import QueryDict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def replace_seasonal_worker_scheme(text):
    pattern = r"seasonal\s*worker\s*scheme"
    updated_text = re.sub(pattern, "sws", text, flags=re.IGNORECASE)
    return updated_text


def dict_to_querydict(data):
    formatted_data = []
    for key, value in data.items():
        if value is None:
            formatted_data.append(f"{key}=")
        elif isinstance(value, list):
            if value:
                for v in value:
                    formatted_data.append(f"{key}={v}")
            else:
                formatted_data.append(f"{key}=")
        else:
            formatted_data.append(f"{key}={value}")

    result = "&".join(formatted_data)
    return QueryDict(result)

def get_date_13_months_ago():
    today = date.today()
    thirteen_months_ago = today - relativedelta(months=13)
    return date(thirteen_months_ago.year, thirteen_months_ago.month, 1)