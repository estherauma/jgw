def capitalize_string(string, separator):
    words = string.split(separator)
    return ' '.join(word.capitalize() for word in words)

def change_dictionary_to_list_of_dictionaries(dictionary):
    data = [dictionary]
    
    list_of_dicts = []
    for item in data:
        dict_item = {}
        for key, value in item.items():
            if isinstance(value, list):
                dict_item[capitalize_string(key, "_")] = ', '.join(value)
            else:
                dict_item[capitalize_string(key, "_")] = value
        list_of_dicts.append(dict_item)
    
    return list_of_dicts