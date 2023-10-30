import re

def replace_seasonal_worker_scheme(text):
    pattern = r'seasonal\s*worker\s*scheme'
    updated_text = re.sub(pattern, 'sws', text, flags=re.IGNORECASE)
    return updated_text
