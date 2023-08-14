def normalize_age(age):

    prefer_not_to_answer = "prefer not to answer"
    
    patterns_to_replace = {
        "not specified": prefer_not_to_answer,
    }
    
    return patterns_to_replace.get(age, age)