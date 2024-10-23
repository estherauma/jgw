from django.db import transaction
from django.db.models import Q,F
from django.db.models.functions import Replace
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.const.localization_const import meassaging_question_response_localization
from common.helpers.model_helpers.preference import (
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
    get_or_add_language_to_db,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
    get_or_add_route_to_db,
)
from common.helpers.preference_helpers.country import get_data_destination, get_data_origin
from common.logger import KunfuPandaLogger

from common.services.api_client import JustGoodWorkAPIClient, MessagingAPIClient
from common.utils.date_utils import todays_date
from question.models import (
    MessagingQuestion,
    MessagingQuestionResponse,
    MessagingQuestionStandard,
    MessagingQuestionText,
    MessagingResponse,
    MessagingResponseOptionText,
)
from preference.models import Country, Organisation, Preference
from question.tasks import translate_and_clean_messaging_question_fields


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/messaging_question_tasks.log")


def fetch_legacy_messaging_question_from_api(client):
    start_date = "2020-11-01"
    end_date = "2022-11-31"

    latest_inlinequestion = MessagingQuestionStandard.objects.last()
    if latest_inlinequestion:
        start_date = latest_inlinequestion.created_at.strftime("%Y-%m-%d")

    return client.get_data(f"/messaging-questions?startDate={start_date}&endDate={end_date}")


def fetch_messaging_question_from_api(client):
    start_date = "2023-11-01"
    end_date = todays_date()

    # get the last time inline question were fetched
    latest_inlinequestion = MessagingQuestionStandard.objects.last()
    if latest_inlinequestion:
        start_date = latest_inlinequestion.created_at.strftime("%Y-%m-%d")

    return client.get_data(f"/question-responses?startDate={start_date}&endDate={end_date}")


@transaction.atomic
def fetch_messaging_questions_from_api_to_db():
    messaging_questions = []

    # legacy
    lagacy_jgw_api_client = JustGoodWorkAPIClient()
    legacy_messaging_questions_resp = fetch_legacy_messaging_question_from_api(lagacy_jgw_api_client)
    messaging_questions.extend(legacy_messaging_questions_resp)

    # new
    jgw_api_client = MessagingAPIClient()
    messaging_questions_resp = fetch_messaging_question_from_api(jgw_api_client)
    messaging_questions.extend(messaging_questions_resp)

    for messaging_question in messaging_questions:
        try:
            add_messaging_question_to_db(messaging_question)
        except Exception as e:
            print("An error occurred during inline questions creation:", str(e))
            transaction.set_rollback(True)
            raise
    kunfu_panda_logger.info(f"Added {len(messaging_questions)} messaging questions to the database")

    # call to translate, question text, response
    translate_and_clean_messaging_question_fields()
    update_translations_from_localization(meassaging_question_response_localization)
    update_myvoice_messaging_questions()

def add_messaging_question_to_db(messaging_question):
    if MessagingQuestionStandard.objects.filter(data_source_id=messaging_question.get("_id")).exists():
        return

    route = messaging_question.get("route")
    location_of_potential_work = messaging_question.get("location_of_potential_work")
    origin = get_data_origin(
        route=route, api_origin=messaging_question.get("origin") or messaging_question.get("locale")
    )
    destination = get_data_destination(
        route=route,
        api_destination=messaging_question.get("destination"),
        location_of_potential_work=location_of_potential_work,
    )

    organisation_sector = messaging_question.get("organisationSector")
    language = messaging_question.get("language")
    organisation = messaging_question.get("organisation")
    factory_farm = messaging_question.get("factoryFarm")
    route_data = get_or_add_route_to_db(route)
    language_data = get_or_add_language_to_db(language)
    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)
    organisation_data = get_or_add_organisation_to_db(organisation)
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)

    # save the standard fields,
    device_id = messaging_question.get("deviceId")
    preference = Preference.objects.filter(device_id=device_id).first()

    messaging_question_standard = MessagingQuestionStandard.objects.create(
        data_source_id=messaging_question.get("_id"),
        device_id=messaging_question.get("deviceId"),
        preference=preference,
        app_id=messaging_question.get("appId"),
        locale=messaging_question.get("locale"),
        api_created_at=messaging_question.get("createdAt"),
        api_updated_at=messaging_question.get("updatedAt"),
        message_id=messaging_question.get("messageId"),
        question_id=messaging_question.get("questionId"),
        route=route_data,
        language=language_data,
        origin=origin_data,
        destination=destination_data,
        organisation_sector=organisation_sector_data,
        organisation=organisation_data,
        factory_farm=factory_farm_data,
    )

    #  create messaging question text
    messaging_question_text = messaging_question.get("questionText")
    if messaging_question_text and isinstance(messaging_question_text, list):
        messaging_question_text = messaging_question_text[0]

    messaging_question_text_object, _ = MessagingQuestionText.objects.get_or_create(
        text=messaging_question_text,
    )

    new_messaging_question = MessagingQuestion.objects.create(
        question=messaging_question_text_object, messaging_question_standard=messaging_question_standard
    )

    # saving responses from the legacy system
    question_responses = (
        messaging_question.get("questionResponse")
        or messaging_question.get("questionValue")
        or messaging_question.get("questionvalue")
    )
    if question_responses:
        if isinstance(question_responses, str):
            messaging_question_response_option_object, _ = MessagingResponseOptionText.objects.get_or_create(
                option=question_responses,
            )

            new_question_response = MessagingResponse.objects.create(
                option=messaging_question_response_option_object, value=question_responses
            )
            messaging_question_response = MessagingQuestionResponse.objects.create(
                messaging_question=new_messaging_question,
            )
            messaging_question_response.responses.add(new_question_response)

        if isinstance(question_responses, list):
            messaging_question_response = MessagingQuestionResponse.objects.create(
                messaging_question=new_messaging_question,
            )
            for response_option in question_responses:
                messaging_question_response_option_object, _ = (
                    MessagingResponseOptionText.objects.get_or_create(
                        option=response_option.get("value"),
                    )
                )
                new_question_response = MessagingResponse.objects.create(
                    option=messaging_question_response_option_object, value=response_option.get("isChecked")
                )
                messaging_question_response.responses.add(new_question_response)

def update_translations_from_localization(localization_data):
    try:
        for response_option in MessagingResponseOptionText.objects.filter(translated_option__contains="&#39;"):
            response_option.translated_option = response_option.translated_option.replace("&#39;", "'")
            response_option.save()
        for entry in localization_data:
            auto_translation = entry['auto_translation']
            correct_translation = entry['correct_translation']
            
            response_option = MessagingResponseOptionText.objects.filter(
                Q(option=auto_translation) | Q(translated_option=auto_translation)
            ).first()

            if response_option:
                response_option.translated_option = correct_translation
                response_option.save()
                print(f"Updated '{auto_translation}' to '{correct_translation}' for id: {response_option.id}")
            else:
                
    except Exception as e:
        print(f"Error during translation update: {str(e)}")

def update_myvoice_messaging_questions():
    with transaction.atomic():
        not_specified_org = Organisation.objects.get(name='not specified')
        myvoice_org = Organisation.objects.get(name='myvoice')
        malaysia_country = Country.objects.get(name='malaysia')

        messaging_questions_to_update = MessagingQuestionStandard.objects.filter(
            organisation=not_specified_org,
            destination=malaysia_country
        )

        updated_count = messaging_questions_to_update.update(
            organisation=myvoice_org,
            is_myvoice_organisation=True
        )

    return updated_count

def reverse_myvoice_messaging_questions():
    with transaction.atomic():

        not_specified_org = Organisation.objects.get(name='not specified')

        messaging_questions_to_reverse = MessagingQuestionStandard.objects.filter(
            is_myvoice_organisation=True
        )

        updated_count = messaging_questions_to_reverse.update(
            organisation=not_specified_org,
            is_myvoice_organisation=False
        )

    return updated_count