
from common.const.value_const import NOT_SPECIFIED


# def event_name_mapping(event_name: str):
#     print(event_name)

#     prefer_not_to_answer = "prefer not to answer"
    

    
#     if event_name is None:
#         return prefer_not_to_answer.lower()
    
#     normalize_event_name = patterns_to_replace.get(event_name.lower(), event_name)
    
#     if not normalize_event_name.strip():
#         normalize_event_name = NOT_SPECIFIED
        
#     return normalize_event_name

events_name_patterns_to_replace = {
    "ChapterOpened_1_1": "Thinking about it", 
    "ChapterOpened_1_2": "Why come to work in the country", 
    "ChapterOpened_1_3": "Culture and community", 
    "ChapterOpened_1_4": "Type of work available",
    "ChapterOpened_1_5": "Your skills and qualifications", 
    "ChapterOpened_2_1": "Application process",
    "ChapterOpened_2_10": "Agents", 
    "ChapterOpened_2_11": "Travel", 
    "ChapterOpened_2_12": "Immigration", 
    "ChapterOpened_2_2": "Fees and charges",
    "ChapterOpened_2_3": "Equality",
    "ChapterOpened_2_4": "Immigration and visa requirements", 
    "ChapterOpened_2_5": "Visa fees and costs", 
    "ChapterOpened_2_6": "Contract and rights", 
    "ChapterOpened_2_7": "Medical screening", 
    "ChapterOpened_2_8": "Pre employment training", 
    "ChapterOpened_2_9": "Your personal documents", 
    "ChapterOpened_3_1": "Employment status", 
    "ChapterOpened_3_10": "Universal credits and other benefits", 
    "ChapterOpened_3_11": "Personal", 
    "ChapterOpened_3_12": "Transport", 
    "ChapterOpened_3_13": "Everyday life", 
    "ChapterOpened_3_14": "Medical care",
    "ChapterOpened_3_2": "Pay", 
    "ChapterOpened_3_3": "Working hours", 
    "ChapterOpened_3_4": "Holidays and sick leave", 
    "ChapterOpened_3_5": "Health and safety", 
    "ChapterOpened_3_6": "Complaints and grievances", 
    "ChapterOpened_3_7": "Resignation and dismisal", 
    "ChapterOpened_3_8": "Trade Unions", 
    "ChapterOpened_3_9": "Accomodation", 
    "ChapterOpened_about_jgw":"About Just Good Work",
    "ChapterOpened_pp":"Privacy Policy",
    "ChapterOpened_1_7":"Domestic Workers",
    "ChapterOpened_1_6":"Weather",
    "ChapterOpened_2_15":"Changing Jobs (or leaving)",
    
}

chapter_tittle_match_to_chapter_ids=[
{"key":"1_1","chapter_text":"Questions You Need to Ask","destination":"malaysia"},
{"key":"1_2","chapter_text":"Your skills and Qualifications","destination":"malaysia"},
{"key":"1_3","chapter_text":"Fees and Charges","destination":"malaysia"},
{"key":"1_4","chapter_text":"Before You Travel","destination":"malaysia"},
{"key":"2_1","chapter_text":"Job Offer","destination":"malaysia"},
{"key":"2_10","chapter_text":"Changing Jobs","destination":"malaysia"},
{"key":"2_11","chapter_text":"Raising a Grievance","destination":"malaysia"},
{"key":"2_12","chapter_text":"Leaving Malaysia","destination":"malaysia"},
{"key":"2_2","chapter_text":"Contract","destination":"malaysia"},
{"key":"2_3","chapter_text":"Visas","destination":"malaysia"},
{"key":"2_4","chapter_text":"Children in the Workplace","destination":"malaysia"},
{"key":"2_5","chapter_text":"Arrival in Malaysia","destination":"malaysia"},
{"key":"2_6","chapter_text":"Wages","destination":"malaysia"},
{"key":"2_7","chapter_text":"working Hours","destination":"malaysia"},
{"key":"2_8","chapter_text":"Time off and Holidays","destination":"malaysia"},
{"key":"2_9","chapter_text":"Working Conditions","destination":"malaysia"},
{"key":"3_1","chapter_text":"Culture and Religion","destination":"malaysia"},
{"key":"3_2","chapter_text":"Weather","destination":"malaysia"},
{"key":"3_3","chapter_text":"Migran Workers in Malaysia","destination":"malaysia"},
{"key":"3_4","chapter_text":"Women: Risks and Resources","destination":"malaysia"},
{"key":"3_5","chapter_text":"Your Personal Documents","destination":"malaysia"},
{"key":"3_6","chapter_text":"Personal","destination":"malaysia"},
{"key":"3_7","chapter_text":"Medical","destination":"malaysia"},
{"key":"3_8","chapter_text":"Places of Worship","destination":"malaysia"},
{"key":"3_13","chapter_text":"Leaving Malaysia","destination":"malaysia"}
]