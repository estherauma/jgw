import requests
from django.db import transaction
from events.models import Chapter, ChaptersFeedback, ChaptersFeedbackStandard, ImmigrationStatusChapterTitle

from jgwpandas.settings import JGW_API, JGW_API_SECRET
from preference.models import Country, ImmigrationStatus


def fetch_data_from_api(destination_codes):

    url = f"{JGW_API}appcontent/v2/chapter-titles"
    
    combined_data = []

    for code in destination_codes:
        params = {
            "configVersion": "version_4",
            "languageCode": "en-gc",
            "destinationCode": code,
        }

        headers = {
            "secret": JGW_API_SECRET
        }

        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                combined_data.extend(data["data"])
        else:
            print(
                f"Error: Failed to fetch data for destination code {code}. Status code: {response.status_code}"
            )

    return combined_data


def extract_relevant_data(combined_data):

    chapters_list = []
    for destination in combined_data:
        destination_name = destination["destinationName"]
        for chapter in destination["chapters"]:
            chapter_info = {
                "immigrationStatus": destination["immigrationStatus"],
                "destinationName": destination_name,
                "jgwDestinationCode": chapter["documentId"],
                "uid": chapter["uid"],
                "title": chapter["title"],
            }
            chapters_list.append(chapter_info)

    return chapters_list


def filter_unique_chapters(chapters_list):

    unique_chapters = []
    seen_combinations = set()
    for chapter in chapters_list:
        transformed_uid = chapter["uid"].replace(".", "_")
        jgw_code = chapter["jgwDestinationCode"]
        if "jgw-saudi-arabia" in jgw_code:
            transformed_destination_name = "saudi arabia"
        elif "jgw-uae" in jgw_code:
            transformed_destination_name = "united arab emirates"
        elif "jgw-qatar" in jgw_code:
            transformed_destination_name = "qatar"
        elif "jgw-verite-jordan" in jgw_code:
            transformed_destination_name = "jordan"
        elif "jgw-uk" in jgw_code:
            transformed_destination_name = "united kingdom"
        elif "jgw-malaysia" in jgw_code:
            transformed_destination_name = "malaysia"
        elif "jgw-spain" in jgw_code:
            transformed_destination_name = "spain"
        elif "jgw-jersey" in jgw_code:
            transformed_destination_name = "jersey"
        elif "jgw-poland" in jgw_code:
            transformed_destination_name = "poland"
        elif "jgw-mexico" in jgw_code:
            transformed_destination_name = "mexico"
        else:
            transformed_destination_name = None

        combination = (transformed_uid, transformed_destination_name, chapter["title"])
        if combination not in seen_combinations:
            unique_chapters.append(
                {
                    "jgwDestinationCode": jgw_code,
                    "destinationName": transformed_destination_name,
                    "uid": transformed_uid,
                    "title": chapter["title"],
                }
            )
            seen_combinations.add(combination)
    return unique_chapters


def update_or_create_chapters(unique_chapters):

    for chapter_data in unique_chapters:
        try:

            destination = Country.objects.get(name=chapter_data["destinationName"])

            chapter, created = Chapter.objects.update_or_create(
                number_key=chapter_data["uid"],
                destination=destination,
                defaults={"chapter_text": chapter_data["title"]},
            )
            if created:
                print(f"Created new chapter: {chapter_data['uid']}")
            else:
                print(f"Updated existing chapter: {chapter_data['uid']}")
        except Country.DoesNotExist:
            print(f"Destination {chapter_data['destinationName']} does not exist.")
        except Exception as e:
            print(f"Error processing chapter {chapter_data['uid']}: {e}")


def update_chapter_titles():
    fetch_and_update_all_destiantion_chapter_titles()
    update_feedback_titles_for_united_kingdom_and_malaysia()


def fetch_and_update_all_destiantion_chapter_titles():
    destination_codes = ["JOR", "MYS", "MUS", "POL", "QAT", "ROU", "SAU", "ARE", "GBR", "ESP","MEX","JEY"]
    api_data = fetch_data_from_api(destination_codes)
    if api_data:
        chapters_list = extract_relevant_data(api_data)
        unique_chapters = filter_unique_chapters(chapters_list)
        update_or_create_chapters(unique_chapters)


def update_feedback_titles_for_united_kingdom_and_malaysia():
    old_feedback_titles_uk = ["3_7", "3_8", "3_9", "3_10", "3_11", "3_12", "3_13", "3_14"]
    new_feedback_titles_uk = ["2_15", "2_16", "3_1", "3_2", "3_3", "3_4", "3_5", "3_6"]
    feedback_title_mapping_uk = dict(zip(old_feedback_titles_uk, new_feedback_titles_uk))

    old_feedback_titles_malaysia = ["3_13"]
    new_feedback_titles_malaysia = ["2_12"]
    feedback_title_mapping_malaysia = dict(zip(old_feedback_titles_malaysia, new_feedback_titles_malaysia))

    united_kingdom = Country.objects.get(name="united kingdom")
    malaysia = Country.objects.get(name="malaysia")
    with transaction.atomic():
        feedbacks_uk = ChaptersFeedbackStandard.objects.filter(
            feedback_title__in=old_feedback_titles_uk, destination=united_kingdom
        )

        for feedback in feedbacks_uk:
            old_title = feedback.feedback_title
            new_title = feedback_title_mapping_uk.get(old_title)
            if new_title:
                feedback.feedback_title = new_title
                feedback.save()
                print(
                    f"Updated feedback_title from {old_title} to {new_title} for id {feedback.id} in United Kingdom"
                )

                chapter_instance = Chapter.objects.filter(
                    number_key=new_title, destination=united_kingdom
                ).first()
                ChaptersFeedback.objects.filter(feedback_standard=feedback).update(chapter=chapter_instance)
                print(
                    f"Updated chapter to {new_title} for feedback_standard id {feedback.id} in United Kingdom"
                )

        feedbacks_malaysia = ChaptersFeedbackStandard.objects.filter(
            feedback_title__in=old_feedback_titles_malaysia, destination=malaysia
        )

        for feedback in feedbacks_malaysia:
            old_title = feedback.feedback_title
            new_title = feedback_title_mapping_malaysia.get(old_title)
            if new_title:
                feedback.feedback_title = new_title
                feedback.save()
                print(
                    f"Updated feedback_title from {old_title} to {new_title} for id {feedback.id} in Malaysia"
                )

                chapter_instance = Chapter.objects.filter(number_key=new_title, destination=malaysia).first()
                ChaptersFeedback.objects.filter(feedback_standard=feedback).update(chapter=chapter_instance)
                print(f"Updated chapter to {new_title} for feedback_standard id {feedback.id} in Malaysia")


def fetch_data_by_immigration_status(destination_code, immigration_status):
    url = f"{JGW_API}appcontent/v2/chapter-titles"
    
    params = {
        "configVersion": "version_4",
        "languageCode": "en-gc",
        "destinationCode": destination_code,
        "immigrationStatus": immigration_status
    }

    headers = {
        "secret": JGW_API_SECRET
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            return data["data"]
    else:
        print(
            f"Error: Failed to fetch data for destination {destination_code} and immigration status {immigration_status}. Status code: {response.status_code}"
        )
    return []


def update_chapters_by_immigration_status():
    # Get all immigration status instances for United Kingdom(GBR)
    destinationCode = "GBR"
    try:
        immigration_statuses = ImmigrationStatus.objects.all()
        
        for immigration_status in immigration_statuses:
            print(f"Fetching chapters for immigration status: {immigration_status.name}")
            api_data = fetch_data_by_immigration_status(destinationCode, immigration_status.value)
            
            if api_data:
                chapters_list = extract_relevant_data(api_data)
                update_or_create_immigration_status_chapter_titles(chapters_list)
                print(f"Successfully updated chapters for immigration status: {immigration_status.name}")
            else:
                print(f"No data found for immigration status: {immigration_status.name}")
                
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def update_or_create_immigration_status_chapter_titles(chapters_list):

    for chapter_data in chapters_list:
        try:

            destination = Country.objects.filter(name__iexact=chapter_data["destinationName"]).first()
            if not destination:
                raise Country.DoesNotExist
            immigration_status = ImmigrationStatus.objects.get(name=chapter_data["immigrationStatus"])

            chapter, created = ImmigrationStatusChapterTitle.objects.update_or_create(
                chapter_uid=chapter_data["uid"],
                destination=destination,
                immigration_status=immigration_status,
                chapter_title=chapter_data["title"],
                documentId=chapter_data["jgwDestinationCode"]
            )
            if created:
                print(f"Created new immigration status chapter title: {chapter_data['uid']}")
            else:
                print(f"Updated existing immigration status chapter title: {chapter_data['uid']}")
        except Country.DoesNotExist:
            print(f"Destination {chapter_data['destinationName']} does not exist.")
        except Exception as e:
            print(f"Error processing chapter {chapter_data['uid']}: {e}")