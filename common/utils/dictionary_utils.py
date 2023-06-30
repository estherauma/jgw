def change_dictionary_keys_lowercase(dictionary):
    return {key.lower(): value for key, value in dictionary.items()}


def convert_nested_dictionary_keys_to_uppercase(dictionary):
    data_uppercase = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            data_uppercase[key] = {inner_key.upper(): inner_value for inner_key, inner_value in value.items()}
        else:
            data_uppercase[key] = value
    return data_uppercase