import re
from django.db import transaction
from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED

from common.helpers.model_helpers.preference import (
    get_or_add_age_to_db,
    get_or_add_country_state_to_db,
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
    get_or_add_gender_to_db,
    get_or_add_language_to_db,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
)
from common.helpers.preference_helpers.country import get_data_destination, get_data_origin
from common.logger import KunfuPandaLogger
from common.utils.date_utils import date_to_datetime, todays_date
from events.models import Chapter, ChaptersOpened
from preference.models import Preference
from preference.tasks import translate_and_clean_preferences_fields


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/chapters_opened.log")


def fetch_chatpter_opened_from_api():
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    # get the last time preferences were fetched
    latest_chapter_opened = ChaptersOpened.objects.last()
    if latest_chapter_opened:
        start_date = latest_chapter_opened.created_at.strftime("%Y-%m-%d")

    appEvents = AppEvents()
    chapters_events_result = appEvents.bigquery_chapters_data(start_date=start_date, end_date=end_date)
    return chapters_events_result


def get_chapter_number_from_name(chapter_name):
    matches = re.search(r"ChapterOpened_(\d+_\d+)", chapter_name)
    return matches.group(1) if matches else chapter_name


@transaction.atomic
def fetch_chapters_opened_data_from_api_to_db():
    chapters_opened = fetch_chatpter_opened_from_api() or []

    for chapter_opened in chapters_opened:
        try:
            add_chapters_opened_to_db(chapter_opened)
        except Exception as e:
            KunfuPandaLogger.error(f"An error occurred during preference creation: {str(e)}")
            transaction.set_rollback(True)
            raise

    kunfu_panda_logger.info(f"Added {len(chapters_opened)} chapters opened to the database")

    # call celery to the translate, gender, language and sector of work functions
    translate_and_clean_preferences_fields()


def add_chapters_opened_to_db(chapters_feedback):
    event_name = chapters_feedback.get("event_name")
    event_date = chapters_feedback.get("event_date")

    age = chapters_feedback.get("age")
    language = chapters_feedback.get("language")
    gender = chapters_feedback.get("gender")
    organisation_sector = chapters_feedback.get("organisationSector")
    organisation = chapters_feedback.get("organisation")
    destination_state = chapters_feedback.get("destinationState")

    device_id = chapters_feedback.get("deviceId")
    app_id = chapters_feedback.get("appId")
    route = chapters_feedback.get("route")
    location_of_potential_work = chapters_feedback.get("location_of_potential_work")
    factory_farm = chapters_feedback.get("factoryFarm")

    origin = get_data_origin(
        route=route, api_origin=chapters_feedback.get("locale") or chapters_feedback.get("origin")
    )
    destination = get_data_destination(
        route=route,
        api_destination=chapters_feedback.get("destination"),
        location_of_potential_work=location_of_potential_work,
    )

    language_data = get_or_add_language_to_db(language)
    age_data = get_or_add_age_to_db(age)
    destination_state_data = get_or_add_country_state_to_db(destination_state)
    organisation_data = get_or_add_organisation_to_db(organisation)
    gender_data = get_or_add_gender_to_db(gender)
    organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)

    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)

    # save the related preference,
    preference = Preference.objects.filter(device_id=device_id).first()

    chapter_opened = ChaptersOpened.objects.create(
        event_name=event_name or NOT_SPECIFIED,
        organisation=organisation_data,
        event_created_at=date_to_datetime(event_date),
        age=age_data,
        language=language_data,
        gender=gender_data,
        organisation_sector=organisation_sector_data,
        device_id=device_id,
        app_id=app_id,
        destination_state=destination_state_data,
        destination=destination_data,
        origin=origin_data,
        preference=preference,
        factory_farm=factory_farm_data,
    )
    chapter, _ = Chapter.objects.get_or_create(
        number_key=get_chapter_number_from_name(chapter_opened.event_name)
    )
    chapter_opened.chapter = chapter
    chapter_opened.save()
