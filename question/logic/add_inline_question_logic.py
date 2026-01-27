from django.db import transaction
import re
import requests
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.const.localization_const import inline_question_response_localization
from common.custom_libs.google_translate import pandas_translator_translate
from common.helpers.model_helpers.preference import (
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
    get_or_add_immigration_status_to_db,
    get_or_add_language_to_db,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
    get_or_add_route_to_db,
)
from common.logger import KunfuPandaLogger
from common.services.api_client import JustGoodWorkAPIClient

from common.utils.date_utils import todays_date
from common.helpers.preference_helpers.country import (
    get_data_destination,
    get_data_origin,
)
from preference.utils import format_text_for_db
from question.logic.update_question_data_with_org_info import update_inline_question_org_info_from_organisation
from question.models import (
    FollowUpQuestion,
    FollowupFollowupInlineQuestionResponse,
    FollowupInlineQuestionResponse,
    InlineQuestion,
    InlineQuestionAndKeysMatch,
    InlineQuestionResponse,
    InlineQuestionResponseText,
    InlineQuestionStandard,
    InlineQuestionText,
    LeadInlineQuestionResponse,
    InlineQuestionV1,
    InlineQuestionResponseV1,
    QuestionCategory,
)
from preference.models import Country, Organisation, OrganisationData, Preference, TextTranslations
from question.tasks import translate_and_clean_inline_question_fields

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/inline_question_tasks.log")


def fetch_legacy_inline_question_from_api(client):
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    # get the last time inline question were fetched
    latest_inlinequestion = (
        InlineQuestionStandard.objects.filter(api_version="v1").order_by("-created_at").first()
    )
    if latest_inlinequestion:
        start_date = latest_inlinequestion.created_at.strftime("%Y-%m-%d")

    return client.get_data(f"/inlinequestions?startDate={start_date}&endDate={end_date}")


def fetch_inline_question_v2_from_api(client):

    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    # get the last time inline question were fetched
    latest_inlinequestion = (
        InlineQuestionStandard.objects.filter(api_version="v2").order_by("-created_at").first()
    )
    if latest_inlinequestion:
        start_date = latest_inlinequestion.created_at.strftime("%Y-%m-%d")

    return client.get_data(f"/inlinequestionsv2?startDate={start_date}&endDate={end_date}")


unwanted_fields = [
    "_id",
    "deviceId",
    "appId",
    "locale",
    "route",
    "organisation",
    "organisationSector",
    "factoryFarm",
    "createdAt",
    "updatedAt",
    "__v",
    "age",
    "appVersion",
    "deviceModel",
    "os",
    "osVersion",
    "questionKey",
    "questionSection",
    "questionText",
    "questionValue",
    "sectors",
    "seenTabWelcomeText",
    "destinationRepository",
    "destination",
    "destinationState",
    "gender",
    "language",
    "location_of_potential_work",
    "origin",
]


def fetch_inline_question_v3_from_api(client):
    """
    Fetches inline questions version 3 from the API.

    This function retrieves inline questions data from the API, starting from either
    the application's possible start date or the date of the last fetched question,
    up to the current date.

    Args:
        client: An instance of the API client used to make requests.

    Returns:
        A list of inline questions (version 3) retrieved from the API.
    """

    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    # get the last time inline question were fetched
    latest_inlinequestion = (
        InlineQuestionStandard.objects.filter(api_version="v3").order_by("-created_at").first()
    )
    if latest_inlinequestion:
        start_date = latest_inlinequestion.created_at.strftime("%Y-%m-%d")

    return client.get_data(f"/inlinequestionsv3?startDate={start_date}&endDate={end_date}")


def separate_inline_question_standard_fields_from_others(inline_question_dict):
    other_fields = []
    standard_fields = {}

    for obj_key, obj_value in inline_question_dict.items():
        if obj_key in unwanted_fields:
            standard_fields[obj_key] = obj_value
        if obj_key not in unwanted_fields:
            other_fields.append({"key": obj_key, "value": obj_value})

    return {"responses_list": other_fields, "standard_fields_dict": standard_fields}


def format_inline_question_response_text(text):
    inline_question_text = text
    if isinstance(text, str):
        if text == "undefined" or text == "" or text == " " or text is None:
            inline_question_text = NOT_SPECIFIED

        cleaned_text = re.sub(r"<br/>", "", inline_question_text)
        return cleaned_text
    return text


def inline_questions_v2_logic(jgw_api_client):
    inline_questions_v2 = fetch_inline_question_v2_from_api(jgw_api_client)

    for inline_question_v2 in inline_questions_v2:
        if isinstance(inline_question_v2, str):
            return

        if InlineQuestionStandard.objects.filter(data_source_id=inline_question_v2.get("_id")).exists():
            return

        preference = Preference.objects.filter(device_id=inline_question_v2.get("deviceId")).first()

        origin = get_data_origin(
            route=inline_question_v2.get("route") or NOT_SPECIFIED,
            api_origin=inline_question_v2.get("locale"),
        )
        destination = get_data_destination(
            route=inline_question_v2.get("route") or NOT_SPECIFIED,
            api_destination=inline_question_v2.get("destination"),
            location_of_potential_work=inline_question_v2.get("location_of_potential_work"),
        )
        immigration_status = inline_question_v2.get("immigrationStatus")

        route_data = get_or_add_route_to_db(inline_question_v2.get("route") or NOT_SPECIFIED)
        language_data = get_or_add_language_to_db(inline_question_v2.get("language"))
        origin_data = get_or_add_country_to_db(origin, source="origin")
        destination_data = get_or_add_country_to_db(destination, source="destination")
        organisation_sector_data = get_or_add_organisation_sector_to_db(
            inline_question_v2.get("organisationSector")
        )
        organisation_data = get_or_add_organisation_to_db(inline_question_v2.get("organisation"))
        factory_farm_data = get_or_add_factory_farm_to_db(inline_question_v2.get("factoryFarm"))
        immigration_status_data = get_or_add_immigration_status_to_db(immigration_status)
        org_code = inline_question_v2.get("organisationCode")
        org_work_code = inline_question_v2.get("organisationAccessCode")
        new_inline_question_standard = InlineQuestionStandard.objects.create(
            data_source_id=inline_question_v2.get("_id"),
            device_id=inline_question_v2.get("deviceId"),
            preference=preference,
            app_id=inline_question_v2.get("appId"),
            locale=inline_question_v2.get("locale"),
            route=route_data,
            language=language_data,
            origin=origin_data,
            destination=destination_data,
            organisation_sector=organisation_sector_data,
            organisation=organisation_data,
            org_code=org_code,
            org_work_code=org_work_code,
            factory_farm=factory_farm_data,
            immigration_status=immigration_status_data,
            api_created_at=inline_question_v2.get("createdAt"),
            api_updated_at=inline_question_v2.get("updatedAt"),
            api_version="v2"
        )

        inline_question_text, _ = InlineQuestionText.objects.get_or_create(
            text=format_inline_question_response_text(inline_question_v2.get("questionKey")),
        )
        inline_question_text.title_text = inline_question_v2.get("questionText")
        inline_question_text.save()

        created_inline_question = InlineQuestion.objects.create(
            question=inline_question_text, inline_question_standard=new_inline_question_standard
        )

        # create inline question response
        qn_resp_text = (
            format_inline_question_response_text(inline_question_v2.get("questionValue")) or NOT_SPECIFIED
        )
        if isinstance(qn_resp_text, dict) and "amount" in qn_resp_text:
            qn_resp_text = qn_resp_text.get("amount")

        # Replace get_or_create with safer approach for TextTranslations
        text_translations = TextTranslations.objects.filter(
            original_text=format_text_for_db(qn_resp_text)
        ).first()
        
        if not text_translations:
            text_translations = TextTranslations.objects.create(
                original_text=format_text_for_db(qn_resp_text)
            )
            
        if not text_translations.translated_text:
            resp_translated = format_text_for_db(pandas_translator_translate(qn_resp_text))
            text_translations.translated_text = resp_translated
            qn_resp_text = resp_translated
            text_translations.save()
        else:
            qn_resp_text = text_translations.translated_text

        # Replace the direct creation with get_or_create logic that handles duplicates
        try:
            inline_question_response_text = InlineQuestionResponseText.objects.get(
                translated_text=qn_resp_text
            )
        except MultipleObjectsReturned:
            # If multiple objects exist, use the first one
            inline_question_response_text = InlineQuestionResponseText.objects.filter(
                translated_text=qn_resp_text
            ).first()
        except InlineQuestionResponseText.DoesNotExist:
            # If no object exists, create a new one
            inline_question_response_text = InlineQuestionResponseText.objects.create(
                translated_text=qn_resp_text
            )

        inline_question_text.title_text = inline_question_v2.get("questionText")
        inline_question_text.save()

        InlineQuestionResponse.objects.create(
            inline_question=created_inline_question, response=inline_question_response_text
        )

    kunfu_panda_logger.info(f"Added {len(inline_questions_v2)} inline questions v2 to the database")


def inline_questions_v3_logic(jgw_api_client):
    inline_questions_v3 = fetch_inline_question_v3_from_api(jgw_api_client)
    for inline_question_v3 in inline_questions_v3:
        if isinstance(inline_question_v3, str):
            continue

        if InlineQuestionStandard.objects.filter(data_source_id=inline_question_v3.get("_id")).exists():
            continue
        try:
            preference = Preference.objects.filter(device_id=inline_question_v3.get("deviceId")).first()

            origin = get_data_origin(
                route=inline_question_v3.get("route") or NOT_SPECIFIED,
                api_origin=inline_question_v3.get("locale"),
            )
            destination = get_data_destination(
                route=inline_question_v3.get("route") or NOT_SPECIFIED,
                api_destination=inline_question_v3.get("destination"),
                location_of_potential_work=inline_question_v3.get("location_of_potential_work"),
            )
            immigration_status = inline_question_v3.get("immigrationStatus")

            route_data = get_or_add_route_to_db(inline_question_v3.get("route") or NOT_SPECIFIED)
            language_data = get_or_add_language_to_db(inline_question_v3.get("language"))
            origin_data = get_or_add_country_to_db(origin, source="origin")
            destination_data = get_or_add_country_to_db(destination, source="destination")
            organisation_sector_data = get_or_add_organisation_sector_to_db(
                inline_question_v3.get("organisationSector")
            )
            organisation_data = get_or_add_organisation_to_db(inline_question_v3.get("organisation"))
            factory_farm_data = get_or_add_factory_farm_to_db(inline_question_v3.get("factoryFarm"))
            immigration_status_data = get_or_add_immigration_status_to_db(immigration_status)
            org_code = inline_question_v3.get("organisationCode")
            org_work_code = inline_question_v3.get("organisationAccessCode")

            new_inline_question_standard = InlineQuestionStandard.objects.create(
                data_source_id=inline_question_v3.get("_id"),
                device_id=inline_question_v3.get("deviceId"),
                preference=preference,
                app_id=inline_question_v3.get("appId"),
                locale=inline_question_v3.get("locale"),
                route=route_data,
                language=language_data,
                origin=origin_data,
                destination=destination_data,
                immigration_status=immigration_status_data,
                organisation_sector=organisation_sector_data,
                organisation=organisation_data,
                org_code=org_code,
                org_work_code=org_work_code,
                factory_farm=factory_farm_data,
                api_created_at=inline_question_v3.get("createdAt"),
                api_updated_at=inline_question_v3.get("updatedAt"),
                api_version="v3",
            )

            question_key = inline_question_v3.get("questionKey")
            question_value = inline_question_v3.get("questionValue")

            # Extract the option value(s) from questionValue
            extracted_value = extract_question_value_option(question_value)

            # Convert extracted_value to string for storage
            if isinstance(extracted_value, list):
                qn_resp_text = ", ".join(map(str, extracted_value))
            else:
                qn_resp_text = str(extracted_value)

            inline_question_text, _ = InlineQuestionText.objects.get_or_create(
                text=format_inline_question_response_text(question_key),
            )
            inline_question_text.title_text = inline_question_v3.get("questionText")
            inline_question_text.save()

            created_inline_question = InlineQuestion.objects.create(
                question=inline_question_text, inline_question_standard=new_inline_question_standard
            )

            # Replace get_or_create with safer approach for TextTranslations
            text_translations = TextTranslations.objects.filter(
                original_text=format_text_for_db(qn_resp_text)
            ).first()
            
            if not text_translations:
                text_translations = TextTranslations.objects.create(
                    original_text=format_text_for_db(qn_resp_text)
                )
                
            if not text_translations.translated_text:
                resp_translated = format_text_for_db(pandas_translator_translate(qn_resp_text))
                text_translations.translated_text = resp_translated
                qn_resp_text = resp_translated
                text_translations.save()
            else:
                qn_resp_text = text_translations.translated_text

            try:
                inline_question_response_text = InlineQuestionResponseText.objects.get(
                    translated_text=qn_resp_text
                )
            except MultipleObjectsReturned:
                inline_question_response_text = InlineQuestionResponseText.objects.filter(
                    translated_text=qn_resp_text
                ).first()
            except InlineQuestionResponseText.DoesNotExist:
                inline_question_response_text = InlineQuestionResponseText.objects.create(
                    translated_text=qn_resp_text
                )

            InlineQuestionResponse.objects.create(
                inline_question=created_inline_question, response=inline_question_response_text
            )
        except Exception as e:
            kunfu_panda_logger.error(f"Error creating inline question response: {e}")

    kunfu_panda_logger.info(f"Added {len(inline_questions_v3)} inline questions v3 to the database")


def inline_questions_v1_logic(jgw_api_client):
    legacy_inline_questions = fetch_legacy_inline_question_from_api(jgw_api_client)

    for inline_question in legacy_inline_questions:
        add_inline_question_to_db(inline_question)

    kunfu_panda_logger.info(f"Added {len(legacy_inline_questions)} inline questions v1 to the database")


@transaction.atomic
def fetch_inline_questions_from_api_to_db():

    jgw_api_client = JustGoodWorkAPIClient()

    # inline question v1 logic
    inline_questions_v1_logic(jgw_api_client)

    # inline question v2 logic
    inline_questions_v2_logic(jgw_api_client)

    # store new v3 inline questions
    store_new_v3_inline_questions(jgw_api_client)

    # #inline question v3 logic
    inline_questions_v3_logic(jgw_api_client)

    # start translation
    translate_and_clean_inline_question_fields()

    # fetch questions keys and names data
    fetch_questions_key_and_name_from_api()

    update_inline_question_response_translations(inline_question_response_localization)
    update_myvoice_inline_questions()
    update_inline_question_org_info_from_organisation()


def add_inline_question_to_db(inline_question):
    if isinstance(inline_question, str):
        return

    if InlineQuestionStandard.objects.filter(data_source_id=inline_question.get("_id")).exists():
        return

    standard_and_other_fields = separate_inline_question_standard_fields_from_others(inline_question)

    standard_fields_dict = standard_and_other_fields.get("standard_fields_dict")
    responses_list = standard_and_other_fields.get("responses_list")

    route = standard_fields_dict.get("route") or NOT_SPECIFIED


    location_of_potential_work = standard_and_other_fields.get("location_of_potential_work")
    origin = get_data_origin(route=route, api_origin=standard_fields_dict.get("locale"))
    destination = get_data_destination(
        route=route,
        api_destination=standard_fields_dict.get("destination"),
        location_of_potential_work=location_of_potential_work,
    )

    language = standard_fields_dict.get("language")
    organisation_sector = standard_fields_dict.get("organisationSector")
    organisation = standard_fields_dict.get("organisation")
    factory_farm = standard_fields_dict.get("factoryFarm")
    immigration_status = standard_fields_dict.get("immigrationStatus")

    route_data = get_or_add_route_to_db(route)
    language_data = get_or_add_language_to_db(language)
    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)
    organisation_data = get_or_add_organisation_to_db(organisation)
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)
    immigration_status_data = get_or_add_immigration_status_to_db(immigration_status)

    # save the standard fields,
    device_id = standard_fields_dict.get("deviceId")
    preference = Preference.objects.filter(device_id=device_id).first()

    inline_question_standard = InlineQuestionStandard.objects.create(
        data_source_id=standard_fields_dict.get("_id"),
        device_id=device_id,
        preference=preference,
        app_id=standard_fields_dict.get("appId"),
        locale=standard_fields_dict.get("locale"),
        route=route_data,
        language=language_data,
        origin=origin_data,
        destination=destination_data,
        immigration_status=immigration_status_data,
        organisation_sector=organisation_sector_data,
        organisation=organisation_data,
        factory_farm=factory_farm_data,
        api_created_at=standard_fields_dict.get("createdAt"),
        api_updated_at=standard_fields_dict.get("updatedAt"),
        api_version="v1",
    )

    #  get or create inline question text
    if "questionKey" in inline_question:
        inline_question_text, _ = InlineQuestionText.objects.get_or_create(
            text=format_inline_question_response_text(inline_question.get("questionKey")),
        )
        inline_question_text.title_text = inline_question.get("questionText")
        inline_question_text.save()

        created_inline_question = InlineQuestion.objects.create(
            question=inline_question_text, inline_question_standard=inline_question_standard
        )

        qn_resp_text = (
            format_inline_question_response_text(inline_question.get("questionValue")) or NOT_SPECIFIED
        )
        if isinstance(qn_resp_text, dict) and "amount" in qn_resp_text:
            qn_resp_text = qn_resp_text.get("amount")

        # Replace get_or_create with safer approach for TextTranslations
        text_translations = TextTranslations.objects.filter(
            original_text=format_text_for_db(qn_resp_text)
        ).first()
        
        if not text_translations:
            text_translations = TextTranslations.objects.create(
                original_text=format_text_for_db(qn_resp_text)
            )
            
        if not text_translations.translated_text:
            resp_translated = format_text_for_db(pandas_translator_translate(qn_resp_text))
            text_translations.translated_text = resp_translated
            qn_resp_text = resp_translated
            text_translations.save()
        else:
            qn_resp_text = text_translations.translated_text

        try:
            inline_question_response_text = InlineQuestionResponseText.objects.get(
                translated_text=qn_resp_text
            )
        except MultipleObjectsReturned:
            inline_question_response_text = InlineQuestionResponseText.objects.filter(
                translated_text=qn_resp_text
            ).first()
        except InlineQuestionResponseText.DoesNotExist:
            inline_question_response_text = InlineQuestionResponseText.objects.create(
                translated_text=qn_resp_text
            )

        inline_question_text.title_text = inline_question.get("questionText")
        inline_question_text.save()

        InlineQuestionResponse.objects.create(
            inline_question=created_inline_question, response=inline_question_response_text
        )
    else:
        for response_list in responses_list:
            inline_question_text, _ = InlineQuestionText.objects.get_or_create(
                text=format_inline_question_response_text(response_list.get("key"))
            )

            created_inline_question = InlineQuestion.objects.create(
                question=inline_question_text, inline_question_standard=inline_question_standard
            )

            # create inline question response
            resp_text = format_inline_question_response_text(response_list.get("value")) or NOT_SPECIFIED
            if isinstance(resp_text, dict) and "amount" in resp_text:
                resp_text = resp_text.get("amount")

            # Replace get_or_create with safer approach for TextTranslations
            text_translations = TextTranslations.objects.filter(
                original_text=format_text_for_db(resp_text)
            ).first()
            
            if not text_translations:
                text_translations = TextTranslations.objects.create(
                    original_text=format_text_for_db(resp_text)
                )
                
            if not text_translations.translated_text:
                resp_translated = format_text_for_db(pandas_translator_translate(resp_text))
                text_translations.translated_text = resp_translated
                resp_text = resp_translated
                text_translations.save()
            else:
                resp_text = text_translations.translated_text

            try:
                inline_question_response_text = InlineQuestionResponseText.objects.get(
                    translated_text=resp_text
                )
            except MultipleObjectsReturned:
                inline_question_response_text = InlineQuestionResponseText.objects.filter(
                    translated_text=resp_text
                ).first()
            except InlineQuestionResponseText.DoesNotExist:
                inline_question_response_text = InlineQuestionResponseText.objects.create(
                    translated_text=resp_text
                )

            InlineQuestionResponse.objects.create(
                inline_question=created_inline_question, response=inline_question_response_text
            )


def fetch_questions_key_and_name_from_api():
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()
    url = f"https://staging-api.justgood.work/api/v2/appcontent/query-documents?type=create_content_area&startDate={start_date}&endDate={end_date}"
    response = requests.get(url)
    if response.status_code == 200:
        questions_data = response.json()
        kunfu_panda_logger.info("Successfully fetched questions data from the API")
        filtered_questions = filter_questions_key_and_name_data(questions_data)
        save_filtered_questions_and_keys(filtered_questions)
        translate_inq()
        update_inline_question_text_with_mapper()
        kunfu_panda_logger.info(f" Found {len(filtered_questions)} matches ")
        return filtered_questions

def translate_and_update_response_text(response_obj, response_text):
    """
    Translates response text to English and updates the response_text_translated field.
    
    Args:
        response_obj: InlineQuestionResponseV1 instance
        response_text: The original response text to translate
    """
    if response_obj and response_text and not response_obj.response_text_translated:
        try:
            translated_text = pandas_translator_translate(response_text)
            if translated_text:
                response_obj.response_text_translated = format_text_for_db(translated_text)
                response_obj.save()
        except Exception as e:
            kunfu_panda_logger.error(f"Error translating response text: {str(e)}")

def fetch_inline_question_new_v3_from_api(client):
    """
    Fetches inline questions version 3 from the API.

    This function retrieves inline questions data from the API, starting from either
    the application's possible start date or the date of the last fetched question,
    up to the current date.

    Args:
        client: An instance of the API client used to make requests.

    Returns:
        A list of inline questions (version 3) retrieved from the API.
    """

    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    try:
        latest_inlinequestion = (
            LeadInlineQuestionResponse.objects.order_by("-api_created_at").first()
        )
        if latest_inlinequestion:
            start_date = latest_inlinequestion.api_created_at.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        kunfu_panda_logger.info(f"Could not query existing records (table may not exist): {str(e)}. Using default start date: {start_date}")

    return client.get_data(f"/inlinequestionsv3?startDate={start_date}&endDate={end_date}")

def update_inline_question_text_with_mapper():
    question_texts = InlineQuestionText.objects.all()
    for question_text in question_texts:
        inqm = InlineQuestionAndKeysMatch.objects.filter(inline_question_key=question_text.text).first()
        if inqm:
            question_text.title_text = inqm.inline_question
            question_text.save()

        fq = FollowUpQuestion.objects.filter(followup_question_key=question_text.text).first()
        if fq:
            question_text.title_text = fq.followup_question
            question_text.save()


def filter_questions_key_and_name_data(questions_data):
    english_questions = []
    other_languages_questions = []

    for item in questions_data.get("data", []):
        if item.get("language", "").startswith("en"):
            for content in item.get("pageContent", []):
                if content and content.get("type") == "questions":
                    english_questions.append({**content, **{"custom_lang": "en"}})

        else:
            for content in item.get("pageContent", []):
                if content and content.get("type") == "questions":
                    other_languages_questions.append(content)

    return [*english_questions, *other_languages_questions]


def translate_inq():
    inline_questions_key_matches = InlineQuestionAndKeysMatch.objects.filter(custom_lang__isnull=True)
    for inline_questions_key_match in inline_questions_key_matches:
        pandas_translator_inline_question_key_match = pandas_translator_translate(
            inline_questions_key_match.inline_question
        )
        inline_questions_key_match.inline_question = pandas_translator_inline_question_key_match
        inline_questions_key_match.custom_lang = "en"
        inline_questions_key_match.save()

    followup_questions = FollowUpQuestion.objects.filter(custom_lang__isnull=True)
    for followup_question in followup_questions:
        pandas_translator_followup = pandas_translator_translate(followup_question.followup_question)
        followup_question.followup_question = pandas_translator_followup
        followup_question.custom_lang = "en"
        followup_question.save()


def save_filtered_questions_and_keys(filtered_questions):

    for question_info in filtered_questions:
        question_info_key = question_info.get("key")
        question_info_text = question_info["question"]
        custom_lang = question_info.get("custom_lang")

        question_mapper = InlineQuestionAndKeysMatch.objects.filter(
            inline_question_key=question_info_key
        ).first()
        if not question_mapper:
            question_mapper = InlineQuestionAndKeysMatch.objects.create(
                inline_question=question_info_text,
                inline_question_key=question_info_key,
                custom_lang=custom_lang,
            )

        question_info_options = question_info.get("options")
        for question_info_option in question_info_options:
            option_follow_up_question = question_info_option.get("followUpQuestion")
            if option_follow_up_question:
                follow_up_question_key = option_follow_up_question.get("key")
                follow_up_question_text = option_follow_up_question.get("question")
                fqe = FollowUpQuestion.objects.filter(
                    inline_question__inline_question=question_info_text,
                    followup_question_key=follow_up_question_key,
                )

                if not fqe:
                    FollowUpQuestion.objects.create(
                        inline_question=question_mapper,
                        followup_question=follow_up_question_text,
                        followup_question_key=follow_up_question_key,
                        custom_lang=custom_lang,
                    )


def update_inline_question_response_translations(localization_data):
    try:
        for localization_entry in localization_data:
            language = localization_entry["language"].lower()
            auto_translation = localization_entry["auto_translation"]
            correct_translation = localization_entry["correct_translation"]

            updated_count = InlineQuestionResponseText.objects.filter(
                Q(translated_text=auto_translation)
            ).update(translated_text=correct_translation)

            if updated_count > 0:
                print(
                    f"Updated: '{auto_translation}' to '{correct_translation}' for {updated_count} record(s)"
                )
            else:
                print(f"No match found for '{auto_translation}' in language '{language}'")

    except Exception as e:
        print(f"Error during translation update: {str(e)}")


def extract_question_value_option(question_value):
    if isinstance(question_value, dict):
        return question_value.get("option")
    elif isinstance(question_value, list):
        return [item.get("option") for item in question_value if isinstance(item, dict)]
    else:
        return question_value


def update_myvoice_inline_questions():
    with transaction.atomic():
        not_specified_org = Organisation.objects.get(name="not specified")
        myvoice_org = Organisation.objects.get(name="myvoice")
        malaysia_country = Country.objects.get(name="malaysia")

        inline_questions_to_update = InlineQuestionStandard.objects.filter(
            organisation=not_specified_org, destination=malaysia_country
        )

        updated_count = inline_questions_to_update.update(
            organisation=myvoice_org, is_myvoice_organisation=True
        )

    return updated_count


def reverse_myvoice_inline_questions():
    with transaction.atomic():

        not_specified_org = Organisation.objects.get(name="not specified")

        inline_questions_to_reverse = InlineQuestionStandard.objects.filter(is_myvoice_organisation=True)

        updated_count = inline_questions_to_reverse.update(
            organisation=not_specified_org, is_myvoice_organisation=False
        )

    return updated_count
    
def extract_question_value_data(question_value):
    """
    Helper function to extract key, option and followup key from question_value.
    
    Args:
        question_value: Can be a dict, list, string, or other type
        
    Returns:
        tuple: (key, option, followup_key)
        - key: For lists, comma-separated keys; for dict, the 'key' field; for strings, 'text_input'
        - option: For lists, semicolon-separated options; for dict, the 'option' field; for strings, the string itself
        - followup_key: The followup question key (only for single dict responses, None for lists)
    """
    key = None
    option = None
    followup_key = None
    
    if isinstance(question_value, dict):
        key = question_value.get('key')
        option = question_value.get('option')
        followup_key = question_value.get('followUpQuestionKey')
    elif isinstance(question_value, list):
        keys = []
        options = []
        followup_keys = []
        
        for item in question_value:
            if isinstance(item, dict):
                item_key = item.get('key')
                item_option = item.get('option')
                item_followup = item.get('followUpQuestionKey')
                
                if item_key:
                    keys.append(item_key)
                if item_option:
                    options.append(item_option)
                if item_followup:
                    followup_keys.append(item_followup)
            else:
                keys.append(str(item))
                options.append(str(item))
        
        key = ', '.join(keys) if keys else 'multiple_selection'
        option = '; '.join(options) if options else ''
        
        followup_key = followup_keys[0] if followup_keys and followup_keys[0] else None
    elif isinstance(question_value, str):
        key = 'text_input'
        option = question_value
    else:
        key = 'unknown'
        option = str(question_value) if question_value is not None else ''
        
    return key, option, followup_key


def store_new_v3_inline_questions(jgw_api_client):
    """
    Stores v3 inline questions in the new chain structure.
    Similar to store_new_v2_messaging_questions but for inline questions.
    """
    inline_questions_v3 = fetch_inline_question_new_v3_from_api(jgw_api_client)

    if inline_questions_v3 is None or not isinstance(inline_questions_v3, list):
        raise ValueError(
            f"Invalid inline questions v3 response type: {type(inline_questions_v3)}"
        )

    if len(inline_questions_v3) == 0:
        kunfu_panda_logger.info("No new inline questions v3 received from API (empty list)")
        return 0

    kunfu_panda_logger.info(f"Fetched {len(inline_questions_v3)} inline questions v3")

    questions_map = {}
    for question in inline_questions_v3:
        if isinstance(question, dict):
            device_id = question.get('deviceId')
            if device_id:
                if device_id not in questions_map:
                    questions_map[device_id] = {}
                questions_map[device_id][question.get('questionKey')] = question

    created_leads = 0
    created_followups = 0
    created_followup_followups = 0

    for question in inline_questions_v3:
        if not isinstance(question, dict):
            continue
        if question.get('isLeadQuestion'):
            try:
                question_value = question.get('questionValue')
                value_key, value_option, followup_key = extract_question_value_data(question_value)

                language_data = get_or_add_language_to_db(question.get("language"))
                destination_data = get_or_add_country_to_db(question.get("destination"), source="destination")
                factory_farm_data = get_or_add_factory_farm_to_db(question.get("factoryFarm"))
                immigration_status_data = get_or_add_immigration_status_to_db(question.get("immigrationStatus"))

                try:
                    organisation_data = None
                    org_code = question.get("organisationCode")
                    org_name = question.get("organisation")
                    
                    if org_code:
                        organisation_data = OrganisationData.objects.filter(org_code=org_code).first()
                    
                    if not organisation_data and org_name:
                        organisation_data = OrganisationData.objects.filter(name=org_name).first()
                    
                    if not organisation_data:
                        organisation_data = OrganisationData.objects.get(name="Organisation Not Specified")
                        
                except Exception as e:
                    kunfu_panda_logger.error(f"Error finding organisation: {e}")
                    organisation_data = OrganisationData.objects.get(name="Organisation Not Specified")

                question_category = None
                question_categories = question.get('questionCategories', [])
                if question_categories and isinstance(question_categories, list) and len(question_categories) > 0:
                    category_code = question_categories[0] if isinstance(question_categories[0], str) else question_categories[0].get('code')
                    category_name = question_categories[0] if isinstance(question_categories[0], str) else question_categories[0].get('name')
                    if category_code:
                        question_category = QuestionCategory.objects.filter(code=category_code).first()
                    elif category_name:
                        question_category = QuestionCategory.objects.filter(name=category_name).first()

                question_response_date = None
                if question.get('questionResponseDate'):
                    question_response_date = parse_datetime(question.get('questionResponseDate'))
                
                api_created_at = parse_datetime(question.get('createdAt')) if question.get('createdAt') else None
                api_updated_at = parse_datetime(question.get('updatedAt')) if question.get('updatedAt') else None

                if LeadInlineQuestionResponse.objects.filter(data_source_id=question.get("_id")).exists():
                    continue

                inline_question_v1, _ = InlineQuestionV1.objects.get_or_create(
                    page_id=question.get('pageId', ''),
                    question_key=question.get('questionKey'),
                    defaults={
                        'page_title': question.get('pageTitle'),
                        'question_text': question.get('questionText'),
                        'question_category': question_category,
                    }
                )

                inline_question_response_v1, _ = InlineQuestionResponseV1.objects.get_or_create(
                    response_key=value_key,
                    response_text=value_option,
                    defaults={
                        'response_text_translated': None,
                    }
                )

                if value_option:
                    translate_and_update_response_text(inline_question_response_v1, value_option)

                lead_response = LeadInlineQuestionResponse.objects.create(
                    data_source_id=question.get('_id'),
                    device_id=question.get('deviceId'),
                    app_id=question.get('appId'),
                    inline_question=inline_question_v1,
                    inline_question_response=inline_question_response_v1,
                    response_value=value_key,
                    organisation=organisation_data,
                    organisation_code=org_code,
                    immigration_status=immigration_status_data,
                    factory_farm=factory_farm_data,
                    language=language_data,
                    destination=destination_data,
                    locale=destination_data,
                    question_response_date=question_response_date,
                    api_created_at=api_created_at,
                    api_updated_at=api_updated_at
                )
                created_leads += 1

                if followup_key:
                    device_id = question.get('deviceId')
                    followup_question = questions_map.get(device_id, {}).get(followup_key)
                    
                    if followup_question:
                        followup_value = followup_question.get('questionValue')
                        f_value_key, f_value_option, f_followup_key = extract_question_value_data(followup_value)

                        f_question_category = None
                        f_question_categories = followup_question.get('questionCategories', [])
                        if f_question_categories and isinstance(f_question_categories, list) and len(f_question_categories) > 0:
                            f_category_code = f_question_categories[0] if isinstance(f_question_categories[0], str) else f_question_categories[0].get('code')
                            f_category_name = f_question_categories[0] if isinstance(f_question_categories[0], str) else f_question_categories[0].get('name')
                            if f_category_code:
                                f_question_category = QuestionCategory.objects.filter(code=f_category_code).first()
                            elif f_category_name:
                                f_question_category = QuestionCategory.objects.filter(name=f_category_name).first()

                        f_question_response_date = None
                        if followup_question.get('questionResponseDate'):
                            f_question_response_date = parse_datetime(followup_question.get('questionResponseDate'))
                        
                        f_api_created_at = parse_datetime(followup_question.get('createdAt')) if followup_question.get('createdAt') else None
                        f_api_updated_at = parse_datetime(followup_question.get('updatedAt')) if followup_question.get('updatedAt') else None

                        if FollowupInlineQuestionResponse.objects.filter(
                            lead_question=lead_response,
                            data_source_id=followup_question.get("_id")
                        ).exists():
                            followup_response = FollowupInlineQuestionResponse.objects.filter(
                                lead_question=lead_response,
                                data_source_id=followup_question.get("_id")
                            ).first()
                        else:
                            f_inline_question_v1, _ = InlineQuestionV1.objects.get_or_create(
                                page_id=followup_question.get('pageId', ''),
                                question_key=followup_question.get('questionKey'),
                                defaults={
                                    'page_title': followup_question.get('pageTitle'),
                                    'question_text': followup_question.get('questionText'),
                                    'question_category': f_question_category,
                                }
                            )

                            f_inline_question_response_v1, _ = InlineQuestionResponseV1.objects.get_or_create(
                                response_key=f_value_key,
                                response_text=f_value_option,
                                defaults={
                                    'response_text_translated': None,
                                }
                            )

                            if f_value_option:
                                translate_and_update_response_text(f_inline_question_response_v1, f_value_option)

                            followup_response = FollowupInlineQuestionResponse.objects.create(
                                lead_question=lead_response,
                                data_source_id=followup_question.get('_id'),
                                device_id=followup_question.get('deviceId'),
                                inline_question=f_inline_question_v1,
                                inline_question_response=f_inline_question_response_v1,
                                response_value=f_value_key,
                                question_response_date=f_question_response_date,
                                api_created_at=f_api_created_at,
                                api_updated_at=f_api_updated_at
                            )
                            created_followups += 1

                        if f_followup_key:
                            followup_followup_question = questions_map.get(device_id, {}).get(f_followup_key)
                            
                            if followup_followup_question:
                                ff_value = followup_followup_question.get('questionValue')
                                ff_value_key, ff_value_option, _ = extract_question_value_data(ff_value)

                                ff_question_category = None
                                ff_question_categories = followup_followup_question.get('questionCategories', [])
                                if ff_question_categories and isinstance(ff_question_categories, list) and len(ff_question_categories) > 0:
                                    ff_category_code = ff_question_categories[0] if isinstance(ff_question_categories[0], str) else ff_question_categories[0].get('code')
                                    ff_category_name = ff_question_categories[0] if isinstance(ff_question_categories[0], str) else ff_question_categories[0].get('name')
                                    if ff_category_code:
                                        ff_question_category = QuestionCategory.objects.filter(code=ff_category_code).first()
                                    elif ff_category_name:
                                        ff_question_category = QuestionCategory.objects.filter(name=ff_category_name).first()

                                ff_question_response_date = None
                                if followup_followup_question.get('questionResponseDate'):
                                    ff_question_response_date = parse_datetime(followup_followup_question.get('questionResponseDate'))
                                
                                ff_api_created_at = parse_datetime(followup_followup_question.get('createdAt')) if followup_followup_question.get('createdAt') else None
                                ff_api_updated_at = parse_datetime(followup_followup_question.get('updatedAt')) if followup_followup_question.get('updatedAt') else None

                                if not FollowupFollowupInlineQuestionResponse.objects.filter(
                                    followup_question=followup_response,
                                    data_source_id=followup_followup_question.get("_id")
                                ).exists():
                                    ff_inline_question_v1, _ = InlineQuestionV1.objects.get_or_create(
                                        page_id=followup_followup_question.get('pageId', ''),
                                        question_key=followup_followup_question.get('questionKey'),
                                        defaults={
                                            'page_title': followup_followup_question.get('pageTitle'),
                                            'question_text': followup_followup_question.get('questionText'),
                                            'question_category': ff_question_category,
                                        }
                                    )

                                    ff_inline_question_response_v1, _ = InlineQuestionResponseV1.objects.get_or_create(
                                        response_key=ff_value_key,
                                        response_text=ff_value_option,
                                        defaults={
                                            'response_text_translated': None,
                                        }
                                    )

                                    if ff_value_option:
                                        translate_and_update_response_text(ff_inline_question_response_v1, ff_value_option)

                                    FollowupFollowupInlineQuestionResponse.objects.create(
                                        followup_question=followup_response,
                                        data_source_id=followup_followup_question.get('_id'),
                                        device_id=followup_followup_question.get('deviceId'),
                                        inline_question=ff_inline_question_v1,
                                        inline_question_response=ff_inline_question_response_v1,
                                        response_value=ff_value_key,
                                        question_response_date=ff_question_response_date,
                                        api_created_at=ff_api_created_at,
                                        api_updated_at=ff_api_updated_at
                                    )
                                    created_followup_followups += 1

            except Exception as e:
                kunfu_panda_logger.error(f"Error processing question {question.get('_id')}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

    kunfu_panda_logger.info(
        "Finished storing new v3 inline questions. "
        f"leads={created_leads}, followups={created_followups}, followup_followups={created_followup_followups}"
    )

    return created_leads + created_followups + created_followup_followups

