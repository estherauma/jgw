def camel_case_to_uppercase_text(camel_case_string):
    result = ""
    for char in camel_case_string:
        if char.isupper() and result:
            result += " "
        result += char.upper()
    return result

import re

def camel_case_to_space_separated(input_str):
    result = re.sub(r'([a-z])([A-Z])', r'\1 \2', input_str)
    result = result.lower()
    return result