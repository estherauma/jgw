import requests
from events.models import Chapter

from preference.models import Country

def fetch_data_from_api(destination_codes):

    url = "https://staging-api.justgood.work/api/v2/appcontent/chapter-titles"
    combined_data = []
    
    for code in destination_codes:
        params = {
            "productID": "vanilla",
            "configVersion": "app_config_v3",
            "languageCode": "en-gc",
            "destinationCode": code
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                combined_data.extend(data["data"])
        else:
            print(f"Error: Failed to fetch data for destination code {code}. Status code: {response.status_code}")
    
    return combined_data

def extract_relevant_data(combined_data):

    chapters_list = []
    for destination in combined_data:
        destination_name = destination["destinationName"]
        for chapter in destination["chapters"]:
            chapter_info = {
                "destinationName": destination_name,
                "uid": chapter["uid"],
                "title": chapter["title"]
            }
            chapters_list.append(chapter_info)

    print("CHAPTERS",len(chapters_list))
    
    return chapters_list

def filter_unique_chapters(chapters_list):

    unique_chapters = []
    seen_combinations = set()
    for chapter in chapters_list:
        # Transform uid and destinationName
        transformed_uid = chapter["uid"].replace('.', '_')
        transformed_destination_name = chapter["destinationName"].lower()
        
        combination = (transformed_uid, transformed_destination_name, chapter["title"])
        if combination not in seen_combinations:
            unique_chapters.append({
                "destinationName": transformed_destination_name,
                "uid": transformed_uid,
                "title": chapter["title"]
            })
            seen_combinations.add(combination)
    
    return unique_chapters

def update_or_create_chapters(unique_chapters):

    for chapter_data in unique_chapters:
        try:
            # Assuming 'Country' model exists and 'destinationName' is matched by name in lowercase
            destination = Country.objects.get(name=chapter_data["destinationName"])
            
            # Update or create the Chapter instance
            chapter, created = Chapter.objects.update_or_create(
                number_key=chapter_data["uid"],
                destination=destination,
                defaults={"chapter_text": chapter_data["title"]}
            )
            if created:
                print(f"Created new chapter: {chapter_data['uid']}")
            else:
                print(f"Updated existing chapter: {chapter_data['uid']}")
        except Country.DoesNotExist:
            print(f"Destination {chapter_data['destinationName']} does not exist.")
        except Exception as e:
            print(f"Error processing chapter {chapter_data['uid']}: {e}")

def fetch_and_update_all_destiantion_chapter_titles():
    destination_codes = ["JOR", "MYS", "MUS", "POL", "QAT", "ROU", "SAU", "ARE", "GBR"]
    api_data = fetch_data_from_api(destination_codes)
    if api_data:
        chapters_list = extract_relevant_data(api_data)
        unique_chapters = filter_unique_chapters(chapters_list)
        update_or_create_chapters(unique_chapters)
