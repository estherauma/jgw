import re
from django.db import transaction
from django.utils import timezone
from django.db.models import Max
from common.app_events import AppEvents
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED

from common.helpers.model_helpers.preference import (
    get_or_add_age_to_db,
    get_or_add_country_state_to_db,
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
    get_or_add_gender_to_db,
    get_or_add_immigration_status_to_db,
    get_or_add_language_to_db,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
)
from common.helpers.preference_helpers.country import get_data_destination, get_data_origin
from common.logger import KunfuPandaLogger
from events.logic.chapter_title_api_data import update_chapter_titles
from events.logic.update_events_data_with_org_info import update_chapters_opened_org_info_from_organisation
from events.models import Chapter, ChaptersOpened, ImmigrationStatusChapterTitle
from preference.models import Country, Organisation, Preference
from preference.tasks import translate_and_clean_preferences_fields


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/chapters_opened.log")


def get_latest_chapter_opened_event_timestamp():
    latest_timestamp = ChaptersOpened.objects.aggregate(Max("event_created_at"))["event_created_at__max"]
    return latest_timestamp


def fetch_chapter_opened_from_bigquery_in_batches(batch_size=5000, last_event_timestamp=None):
    try:
        appEvents = AppEvents()
        chapters_events_result = appEvents.bigquery_chapters_data(
            batch_size=batch_size, last_event_timestamp=last_event_timestamp
        )
    except Exception as e:
        kunfu_panda_logger.error(f"Error fetching data from big query: {str(e)}")
        raise
    return chapters_events_result


def get_chapter_number_from_name(chapter_name):
    matches = re.search(r"ChapterOpened_(\d+_\d+)", chapter_name)
    return matches[1] if matches else chapter_name


def fetch_chapters_opened_data_from_api_to_db():
    try:
        last_event_timestamp = get_latest_chapter_opened_event_timestamp()
    except Exception as e:
        kunfu_panda_logger.error(f"Error getting the last event timestamp in the database: {str(e)}")
        raise
    batch_size = 5000
    total_fetched = 0

    while True:
        chapters_opened = (
            fetch_chapter_opened_from_bigquery_in_batches(
                batch_size=batch_size, last_event_timestamp=last_event_timestamp
            )
            or []
        )
        if not chapters_opened:
            break

        for chapter_opened in chapters_opened:
            try:
                add_chapters_opened_to_db(chapter_opened)
            except Exception as e:
                kunfu_panda_logger.error(f"An error occurred during chapter creation: {str(e)}")
                raise
        last_event_timestamp = max([chapter_opened["event_date"] for chapter_opened in chapters_opened])

        total_fetched += len(chapters_opened)

        kunfu_panda_logger.info(
            f"Processed {len(chapters_opened)} chapters opened fetched in the current batch and total of {total_fetched} fetched now"
        )

    kunfu_panda_logger.info(f"Finished adding a total of {total_fetched} chapters opened to the database")
    
    translate_and_clean_preferences_fields()
    update_chapter_titles()
    update_myvoice_chapters_opened_events()
    update_chapters_opened_org_info_from_organisation()


def add_chapters_opened_to_db(chapters_feedback):
    event_name = chapters_feedback.get("event_name")
    event_date = chapters_feedback.get("event_date")

    age = chapters_feedback.get("age")
    language = chapters_feedback.get("language")
    gender = chapters_feedback.get("gender")
    organisation_sector = chapters_feedback.get("organisationSector")
    organisation = chapters_feedback.get("organisation")
    destination_state = chapters_feedback.get("destinationState")
    immigration_status = chapters_feedback.get("immigrationStatus")
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
    immigration_status_data = get_or_add_immigration_status_to_db(immigration_status)

    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)

    if event_date is not None and timezone.is_naive(event_date):
        event_date = timezone.make_aware(event_date)

    preference = Preference.objects.filter(device_id=device_id).first()

    chapter_opened = ChaptersOpened.objects.create(
        event_name=event_name or NOT_SPECIFIED,
        organisation=organisation_data,
        event_created_at=event_date,
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
        immigration_status=immigration_status_data,
        factory_farm=factory_farm_data,
    )

    number_key = get_chapter_number_from_name(chapter_opened.event_name)
    
    if immigration_status_data:
        number_key_with_dots = number_key.replace('_', '.')
        
        immigration_status_title = ImmigrationStatusChapterTitle.objects.filter(
            chapter_uid__in=[number_key_with_dots],
            destination=destination_data,
            immigration_status=immigration_status_data
        ).first()

        if immigration_status_title:
            chapter_opened.immigration_status_chapter_title = immigration_status_title
        else:
            chapter, _ = Chapter.objects.get_or_create(
                number_key=number_key,
                destination=destination_data
            )
            chapter_opened.chapter = chapter
    else:
        chapter, _ = Chapter.objects.get_or_create(
            number_key=number_key,
            destination=destination_data
        )
        chapter_opened.chapter = chapter

    try:
        chapter_opened.save()
    except Exception as e:
        kunfu_panda_logger.error(f"Error saving chapter opened: {str(e)}")
        raise


def update_myvoice_chapters_opened_events():
    with transaction.atomic():
        not_specified_org = Organisation.objects.get(name="not specified")
        myvoice_org = Organisation.objects.get(name="myvoice")
        malaysia_country = Country.objects.get(name="malaysia")

        chapters_opened_to_update = ChaptersOpened.objects.filter(
            organisation=not_specified_org, destination=malaysia_country
        )

        updated_count = chapters_opened_to_update.update(
            organisation=myvoice_org, is_myvoice_organisation=True
        )

    return updated_count


def reverse_myvoice_chapters_opened_events():
    with transaction.atomic():

        not_specified_org = Organisation.objects.get(name="not specified")

        preferences_to_reverse = ChaptersOpened.objects.filter(is_myvoice_organisation=True)

        updated_count = preferences_to_reverse.update(
            organisation=not_specified_org, is_myvoice_organisation=False
        )

    return updated_count
