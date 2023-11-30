import re


def get_chapters_from_chapter_feedback(chapter_feedback_dictionary):
    filtered_keys = [
        key
        for key in chapter_feedback_dictionary.keys()
        if re.match(r"^\d+_\d+$", key) or key.startswith("1_")
    ]
    return {key: chapter_feedback_dictionary[key] for key in filtered_keys}


def process_chapter_feedback(chapter_feedback_dictionary):
    print("chapter_feedback_dictionary:::", chapter_feedback_dictionary)
    pass


cp_feedback = {
    "_id": "64f2237b636a8f3d130d4c2c",
    "deviceId": "481aad5608104cc4",
    "1_5": {"wasThisHelpful": "smile"},
    "__v": 0,
    "1_1": {"wasThisHelpful": "fake"},
    "1_7": {"wasThisHelpful": "smile"},
}
print(get_chapters_from_chapter_feedback(cp_feedback))
