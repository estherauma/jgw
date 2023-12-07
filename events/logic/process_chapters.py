import re


def get_chapters_from_chapter_feedback(chapter_feedback_dictionary):
    filtered_keys = [
        key
        for key in chapter_feedback_dictionary.keys()
        if re.match(r"^\d+_\d+$", key) or key.startswith("1_")
    ]
    return {key: chapter_feedback_dictionary[key] for key in filtered_keys}


def is_chapter_feedback(chapter_feedback_dictionary):
    return len(get_chapters_from_chapter_feedback(chapter_feedback_dictionary)) > 0

def is_chapter_feedback_key(input_string: str):
    pattern = r'^\d+_\d+$'
    
    if re.match(pattern, input_string):
        return True
    else:
        return False
