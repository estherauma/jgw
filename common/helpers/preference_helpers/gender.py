def normalize_gender_name(gender: str):        
    patterns_to_replace = {
        "man": "male",
        "men": "male",
        "male gender": "male",
        "woman": "female",
        "a woman": "female",
        "women": "female",
        "girl": "female",
        "feminine": "female",
        "better not answer": "prefer not to answer",
        "better not to answer": "prefer not to answer",
        "i prefer not to answer": "prefer not to answer",
        "i do not want to answer": "prefer not to answer",
        "i do not want to answer.": "prefer not to answer",
        "likes to answer": "prefer not to answer",
        "no answer": "prefer not to answer",
        "i don&#39;t want to answer": "prefer not to answer",
        "i don&#39;t want to answer.": "prefer not to answer",
        "prefer to answer": "prefer not to answer",
        "": "prefer not to answer",
        None: "prefer not to answer",
        "another": "other",
        "behavoir": "other",
        "i don&#39;t feel comfortable answering":"prefer not to answer",
        "behavior":"prefer not to answer"
    }
    
    return patterns_to_replace.get(gender.lower(),gender)