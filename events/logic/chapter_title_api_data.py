import requests
from django.db import transaction
from events.models import Chapter, ChaptersFeedback, ChaptersFeedbackStandard

from preference.models import Country


def fetch_data_from_api(destination_codes):

    url = "https://staging-api.justgood.work/api/v2/appcontent/chapter-titles"
    combined_data = []

    for code in destination_codes:
        params = {
            "productID": "vanilla",
            "configVersion": "app_config_v3",
            "languageCode": "en-gc",
            "destinationCode": code,
        }

        response = requests.get(url, params=params)
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
                "destinationName": destination_name,
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
        transformed_destination_name = chapter["destinationName"].lower()

        combination = (transformed_uid, transformed_destination_name, chapter["title"])
        if combination not in seen_combinations:
            unique_chapters.append(
                {
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
    destination_codes = ["JOR", "MYS", "MUS", "POL", "QAT", "ROU", "SAU", "ARE", "GBR", "ESP"]
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
