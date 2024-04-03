import re


def camel_case_to_uppercase_text(camel_case_string):
    result = ""
    for char in camel_case_string:
        if char.isupper() and result:
            result += " "
        result += char.upper()
    return result


def camel_case_to_space_separated(input_str):
    result = re.sub(r"([a-z])([A-Z])", r"\1 \2", input_str)
    result = result.lower()
    return result


def format_thousands_with_commas(number):
    return f"{number:,}"

def space_separated_to_camel_case(input_str):
    words = input_str.split()
    camel_case_string = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    return camel_case_string