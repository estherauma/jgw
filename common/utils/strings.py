def camel_case_to_uppercase_text(camel_case_string):
    result = ""
    for char in camel_case_string:
        if char.isupper() and result:
            result += " "
        result += char.upper()
    return result