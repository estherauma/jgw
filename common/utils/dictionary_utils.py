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

def add_prefix_to_dictionary_keys(dictionary, prefix):
    new_dict = {}
    for key, value in dictionary.items():
        new_key = f'{prefix}_{key}'
        new_dict[new_key] = value
    return new_dict


def combine_dictionaries(*dicts):
    combined_dict = {}

    for dictionary in dicts:
        combined_dict.update(dictionary)

    return combined_dict