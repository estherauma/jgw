def normalize_gender_name(gender: str):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_answer = "prefer not to answer"
    
    patterns_to_replace = {
        "man": male,
        "men": male,
        "male gender": male,
        "woman": female,
        "a woman": female,
        "women": female,
        "girl": female,
        "feminine": female,
        "better not answer": prefer_not_to_answer,
        "better not to answer": prefer_not_to_answer,
        "i prefer not to answer": prefer_not_to_answer,
        "i do not want to answer": prefer_not_to_answer,
        "i do not want to answer.": prefer_not_to_answer,
        "do not want to answer": prefer_not_to_answer,
        "do not want to answer.": prefer_not_to_answer,
        "likes to answer": prefer_not_to_answer,
        "no answer": prefer_not_to_answer,
        "i don&#39;t want to answer": prefer_not_to_answer,
        "i don&#39;t want to answer.": prefer_not_to_answer,
        "prefer to answer": prefer_not_to_answer,
        "": prefer_not_to_answer,
        None: prefer_not_to_answer,
        "another": other,
        "behavior": other,
        "not specified": other,
        "others": other,
        "i don&#39;t feel comfortable answering":prefer_not_to_answer
    }
    
    return patterns_to_replace.get(gender.lower(), gender)