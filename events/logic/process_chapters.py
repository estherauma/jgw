import re
import requests
from common.helpers.preference_helpers.events import chapter_tittle_match_to_chapter_ids
from ..models import Chapter

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
    
def fetch_chapters_data_from_JGW_api():
    url = "https://staging-api.justgood.work/api/v2/appcontent/query-documents?type=create_content_area&startDate=2017-01-01&endDate=2024-04-9"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 

        chapters_data = response.json()  
        filter_chapters_data_from_JGW_api(chapters_data) 

    except requests.exceptions.RequestException as e:
        print("Error fetching data from JGW API:", e)
        return None
    
def filter_chapters_data_from_JGW_api(chapters_data):
    filtered_chapter_data=[]
    for item in chapters_data.get('data', []):
        if item.get('language', '').startswith('en'):    
            language = item.get('language')
            page_title = item.get('pageTitle')
            uid = item.get('uid').replace('.', '_')
            filtered_chapter_data.append({'language': language, 'pageTitle': page_title, 'uid': uid})     
    return filtered_chapter_data              

from events.models import Chapter, Country

def update_chapter_table_with_chapter_tittle(chapter_tittle_match_to_chapter_ids):
    for item in chapter_tittle_match_to_chapter_ids:
        key = item['key']
        destination_name = item['destination']
        title = item['chapter_text']
        
        destination_country = Country.objects.filter(name=destination_name).first()
        
        if destination_country is None:
            print(f"Country {destination_name} not found in the database")
            continue
        
        matching_chapters = Chapter.objects.filter(number_key=key, destination=destination_country)
        
        if matching_chapters.exists():
            for chapter_title_key_match in matching_chapters:
                chapter_title_key_match.chapter_text = title
                chapter_title_key_match.save()
            
                print(f"Updated chapter {key} with title: {title}")
        else:
            print(f"Chapter {key} not found in the database")
