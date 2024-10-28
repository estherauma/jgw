from django.db import transaction

from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.helpers.model_helpers.preference import (
    add_sector_of_work_to_db,
    get_or_add_age_to_db,
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
    get_or_add_gender_to_db,
    get_or_add_language_to_db,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
    get_or_add_route_to_db,
)
from common.logger import KunfuPandaLogger
from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import parse_api_date, todays_date
from common.helpers.preference_helpers.country import (
    get_data_destination,
    get_data_origin,
)
from events.logic.process_chapters import is_chapter_feedback_key
from events.models import (
    ChaptersFeedback,
    ChaptersFeedbackQuestion,
    ChaptersFeedbackResponse,
    ChaptersFeedbackStandard,
    Chapter
)
from events.tasks import translate_and_clean_chapter_feedback_fields
from preference.models import Country, Organisation, Preference


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/chapters_feedback.log")


def fetch_chapters_feedback_from_api(client):
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    # get the last time inline question were fetched
    latest_chapters_feedback = ChaptersFeedbackStandard.objects.last()
    if latest_chapters_feedback:
        start_date = latest_chapters_feedback.created_at.strftime("%Y-%m-%d")

    kunfu_panda_logger.info(f"Fetching chapters feedback from {start_date} to {end_date}")

    return client.get_data(f"/chapter-feedback?startDate={start_date}&endDate={end_date}")


@transaction.atomic
def fetch_chapters_feedback_from_api_to_db():
    jgw_api_client = JustGoodWorkAPIClient()
    chapters_feedback = fetch_chapters_feedback_from_api(jgw_api_client)

    for chapter_feedback in chapters_feedback:
        try:
            add_chapter_feedback_to_db(chapter_feedback)
        except Exception as e:
            print("An error occurred during inline questions creation:", str(e))
            transaction.set_rollback(True)
            raise
    kunfu_panda_logger.info(f"Added {len(chapters_feedback)} chapters feedback to the database")

    translate_and_clean_chapter_feedback_fields()

    update_myvoice_chapters_feedback()
feedback_non_required_fields = [
    "__v",
    "deviceModel",
    "appVersion",
    "os",
    "osVersion",
    "seenTabWelcomeText",
    "destinationRepository",
]
feedback_standard_fields = [
    "_id",
    "deviceId",
    "appId",
    "locale",
    "route",
    "language",
    "organisation",
    "organisationSector",
    "factoryFarm",
    "createdAt",
    "updatedAt",
    "destination",
    "destinationState",
    "location_of_potential_work",
    "age",
    "gender",
    "sectors",
    "origin",
    "immigrationStatus",
    "organisationCode",
    "organisationAccessCode",
    "registrationToken",
    "version"
]


def separate_feedback_standard_fields_from_others(chapter_feedback):
    feedback_list = []
    standard_fields = {}
    non_required_fields = {}
    for obj_key, obj_value in chapter_feedback.items():
        if obj_key in feedback_standard_fields:
            standard_fields[obj_key] = obj_value

        elif obj_key in feedback_non_required_fields:
            non_required_fields[obj_key] = obj_value

        else:
            feedback_list.append({"key": obj_key, "value": obj_value})
            
    return {"feedback_list": feedback_list, "standard_fields_dict": standard_fields}


def add_chapter_feedback_to_db(chapter_feedback):
    chapter_feedback_parts = separate_feedback_standard_fields_from_others(chapter_feedback)
    standard_fields_dict = chapter_feedback_parts["standard_fields_dict"]
    feedback_list = chapter_feedback_parts["feedback_list"]
    
    if not feedback_list:
        return

    route = standard_fields_dict.get("route") or NOT_SPECIFIED

    location_of_potential_work = standard_fields_dict.get("location_of_potential_work")
    origin = get_data_origin(
        route=route, api_origin=standard_fields_dict.get("locale") or standard_fields_dict.get("origin")
    )
    destination = get_data_destination(
        route=route,
        api_destination=standard_fields_dict.get("destination"),
        location_of_potential_work=location_of_potential_work,
    )

    language = standard_fields_dict.get("language")
    organisation_sector = standard_fields_dict.get("organisationSector")
    organisation = standard_fields_dict.get("organisation")
    factory_farm = standard_fields_dict.get("factoryFarm")
    api_created_at = standard_fields_dict.get("createdAt")
    api_updated_at = standard_fields_dict.get("updatedAt")
    locale = standard_fields_dict.get("locale")
    gender = standard_fields_dict.get("gender")
    age = standard_fields_dict.get("age")
    sectors_of_work = standard_fields_dict.get("sectors")

    device_id = standard_fields_dict.get("deviceId")
    preference = Preference.objects.filter(device_id=device_id).first()

    # related fields
    organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)
    organisation_data = get_or_add_organisation_to_db(organisation)
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)
    gender_data = get_or_add_gender_to_db(gender)
    age_data = get_or_add_age_to_db(age)
    language_data = get_or_add_language_to_db(language)
    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    route_data = get_or_add_route_to_db(route)

    for feedback_data in feedback_list:
        feedback_data_key = feedback_data.get("key")

        if not is_chapter_feedback_key(feedback_data_key):
            continue

        feedback_title = feedback_data.get("key")
        feedback_data_value = feedback_data.get("value")
        feedback_data_value_list = list(feedback_data_value.items())

        data_params = {
            "api_created_at": parse_api_date(api_created_at),
            "api_updated_at": parse_api_date(api_updated_at),
            "data_source_id": standard_fields_dict.get("_id"),
            "device_id": device_id,
            "locale": locale,
            "preference": preference,
            "feedback_title": feedback_title,
            "gender": gender_data,
            "age": age_data,
            "language": language_data,
            "origin": origin_data,
            "destination": destination_data,
            "destination_state": destination_data,
            "route": route_data,
            "organisation_sector": organisation_sector_data,
            "factory_farm": factory_farm_data,
            "organisation": organisation_data,
        }

        chapters_feedback_standard = ChaptersFeedbackStandard.objects.create(**data_params)

        for feedback in feedback_data_value_list:
            feedback_data_question = feedback[0]
            feedback_data_question_answer = feedback[1]
            feedback_response, _ = ChaptersFeedbackResponse.objects.get_or_create(
                response=feedback_data_question_answer
            )
            feedback_question, _ = ChaptersFeedbackQuestion.objects.get_or_create(question=feedback_data_question)

            chapter_instance, _ = Chapter.objects.get_or_create(number_key=feedback_data_key, destination=destination_data)

            ChaptersFeedback.objects.create(
                feedback_standard=chapters_feedback_standard,
                feedback_question=feedback_question,
                feedback_response=feedback_response,
                chapter=chapter_instance,
            )

        sec_of_work_list = add_sector_of_work_to_db(sectors_of_work)
        for sec_of_work in sec_of_work_list:
            chapters_feedback_standard.sectors_of_work.add(sec_of_work)


def update_myvoice_chapters_feedback():
    with transaction.atomic():
        not_specified_org = Organisation.objects.get(name='not specified')
        myvoice_org = Organisation.objects.get(name='myvoice')
        malaysia_country = Country.objects.get(name='malaysia')

        bigquery_homepage_events_to_update = ChaptersFeedbackStandard.objects.filter(
            organisation=not_specified_org,
            destination=malaysia_country
        )

        updated_count = bigquery_homepage_events_to_update.update(
            organisation=myvoice_org,
            is_myvoice_organisation=True
        )

    return updated_count

def reverse_myvoice_chapters_feedback():
    with transaction.atomic():

        not_specified_org = Organisation.objects.get(name='not specified')

        preferences_to_reverse = ChaptersFeedbackStandard.objects.filter(
            is_myvoice_organisation=True
        )

        updated_count = preferences_to_reverse.update(
            organisation=not_specified_org,
            is_myvoice_organisation=False
        )

    return updated_count
