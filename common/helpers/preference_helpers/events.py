
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
    "ChapterOpened_1_1": "Thinking about it", # Looking for a job?
    "ChapterOpened_1_2": "Why come to work in the country", # Questions for Agents / Recruiters
    "ChapterOpened_1_3": "Culture and community", # Your skills and qualifications
    "ChapterOpened_1_4": "Type of work available", # Fees and charges
    "ChapterOpened_1_5": "Your skills and qualifications", # Culture and Religion
    "ChapterOpened_2_1": "Application process",
    "ChapterOpened_2_10": "Agents", # Changing jobs
    "ChapterOpened_2_11": "Travel", # Raising a Grievance
    "ChapterOpened_2_12": "Immigration", 
    "ChapterOpened_2_2": "Fees and charges",
    "ChapterOpened_2_3": "Equality",
    "ChapterOpened_2_4": "Immigration and visa requirements", # Your contract and rights
    "ChapterOpened_2_5": "Visa fees and costs", # working conditions
    "ChapterOpened_2_6": "Contract and rights", # Pre-Employment Training
    "ChapterOpened_2_7": "Medical screening", # Your Personal Documents
    "ChapterOpened_2_8": "Pre employment training", # Time off and Holidays
    "ChapterOpened_2_9": "Your personal documents", # Working Conditions
    "ChapterOpened_3_1": "Employment status", # Arrival
    "ChapterOpened_3_10": "Universal credits and other benefits", # Medical
    "ChapterOpened_3_11": "Personal", # Places of worship
    "ChapterOpened_3_12": "Transport", # Leaving The UAE
    "ChapterOpened_3_13": "Everyday life", # Leaving Malaysia
    "ChapterOpened_3_14": "Medical care",
    "ChapterOpened_3_2": "Pay", # Managing your money
    "ChapterOpened_3_3": "Working hours", # Your contract and visa
    "ChapterOpened_3_4": "Holidays and sick leave", # work
    "ChapterOpened_3_5": "Health and safety", 
    "ChapterOpened_3_6": "Complaints and grievances", # wages
    "ChapterOpened_3_7": "Resignation and dismisal", # Time Off and Holidays
    "ChapterOpened_3_8": "Trade Unions", # Resignation and Dismissal
    "ChapterOpened_3_9": "Accomodation", # Personal
    "ChapterOpened_about_jgw":"About Just Good Work",
    "ChapterOpened_pp":"Privacy Policy",
    "ChapterOpened_1_7":"Domestic Workers",
    "ChapterOpened_1_6":"Weather",
    "ChapterOpened_2_15":"Changing Jobs (or leaving)",
    
}

chapter_tittle_match_to_chapter_ids={
    "1_1": "Looking for a job?",
    "1_2": "Questions for Agents / Recruiters",
    "1_3": "Your skills and qualifications",
    "1_4": "Fees and charges",
    "1_5": "Culture and Religion",
    "2_1": "Application process",
    "2_10": "Changing jobs",
    "2_11": "Raising a Grievance",
    "2_12": "Immigration", 
    "2_2": "Fees and charges",
    "2_3": "Equality",
    "2_4": "Your contract and rights",
    "2_5": "working conditions",
    "2_6": "Pre-Employment Training",
    "2_7": "Your Personal Documents",
    "2_8": "Travel",
    "2_9": "Working Conditions",
    "3_1": "Arrival",
    "3_10": "Medical",
    "3_11": "Places of worship",
    "3_12": "Leaving The UAE",
    "3_13": "Leaving Malaysia",
    "3_14": "Medical care",
    "3_2": "Managing your money",
    "3_3": "Your contract and visa",
    "3_4": "work",
    "3_5": "Health and safety", 
    "3_6": "wages",
    "3_7": "Time Off and Holidays",
    "3_8": "Resignation and Dismissal",
    "3_9": "Personal",
    "ChapterOpened_about_jgw":"About Just Good Work",
    "ChapterOpened_pp":"Privacy Policy",
    "1_7":"Domestic Workers",
    "1_6":"Weather",
    "2_15":"Changing Jobs (or leaving)",
    "2_16":"Trade Unions"
}