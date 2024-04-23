import re

from django.http import QueryDict


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
