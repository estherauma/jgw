from django.db import transaction
import re
import requests
import json


from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.custom_libs.google_translate import pandas_translator_translate
from common.helpers.model_helpers.preference import (
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
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
from common.utils.helpers import can_use_cached_data
from common.utils.strings import space_separated_to_camel_case
from preference.utils import format_text_for_db
from question.models import (
    FollowUpQuestion,
    InlineQuestion,
    InlineQuestionAndKeysMatch,
    InlineQuestionResponse,
    InlineQuestionResponseText,
    InlineQuestionStandard,
    InlineQuestionText,
)
from preference.models import Preference, TextTranslations
from question.tasks import translate_and_clean_inline_question_fields
from scripts.load_dev_data import InlineQuestionDataCache

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


def new_inline_questions_logic(jgw_api_client):
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

        route_data = get_or_add_route_to_db(inline_question_v2.get("route") or NOT_SPECIFIED)
        language_data = get_or_add_language_to_db(inline_question_v2.get("language"))
        origin_data = get_or_add_country_to_db(origin, source="origin")
        destination_data = get_or_add_country_to_db(destination, source="destination")
        organisation_sector_data = get_or_add_organisation_sector_to_db(
            inline_question_v2.get("organisationSector")
        )
        organisation_data = get_or_add_organisation_to_db(inline_question_v2.get("organisation"))
        factory_farm_data = get_or_add_factory_farm_to_db(inline_question_v2.get("factoryFarm"))

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
            factory_farm=factory_farm_data,
            api_created_at=inline_question_v2.get("createdAt"),
            api_updated_at=inline_question_v2.get("updatedAt"),
            api_version="v2",
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

        text_translations, _ = TextTranslations.objects.get_or_create(
            original_text=format_text_for_db(qn_resp_text)
        )
        if not text_translations.translated_text:
            resp_translated = format_text_for_db(pandas_translator_translate(qn_resp_text))
            text_translations.translated_text = resp_translated
            qn_resp_text = resp_translated
            text_translations.save()
        else:
            qn_resp_text = text_translations.translated_text

        inline_question_response_text, _ = InlineQuestionResponseText.objects.get_or_create(
            translated_text=qn_resp_text
        )

        inline_question_text.title_text = inline_question_v2.get("questionText")
        inline_question_text.save()

        InlineQuestionResponse.objects.create(
            inline_question=created_inline_question, response=inline_question_response_text
        )

    kunfu_panda_logger.info(f"Added {len(inline_questions_v2)} inline questions v2 to the database")


def legacy_inline_questions_logic(jgw_api_client):
    legacy_inline_questions = fetch_legacy_inline_question_from_api(jgw_api_client)

    for inline_question in legacy_inline_questions:
        add_inline_question_to_db(inline_question)

    kunfu_panda_logger.info(f"Added {len(legacy_inline_questions)} inline questions v1 to the database")


@transaction.atomic
def fetch_inline_questions_from_api_to_db():

    jgw_api_client = JustGoodWorkAPIClient()

    # legacy

    legacy_inline_questions_logic(jgw_api_client)

    # new inline question logic
    new_inline_questions_logic(jgw_api_client)

    # start translation
    translate_and_clean_inline_question_fields()

    #fetch questions keys and names data
    fetch_questions_key_and_name_from_api()



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

    route_data = get_or_add_route_to_db(route)
    language_data = get_or_add_language_to_db(language)
    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)
    organisation_data = get_or_add_organisation_to_db(organisation)
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)

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

        # create inline question response
        qn_resp_text = (
            format_inline_question_response_text(inline_question.get("questionValue")) or NOT_SPECIFIED
        )
        if isinstance(qn_resp_text, dict) and "amount" in qn_resp_text:
            qn_resp_text = qn_resp_text.get("amount")

        text_translations, _ = TextTranslations.objects.get_or_create(
            original_text=format_text_for_db(qn_resp_text)
        )
        if not text_translations.translated_text:
            resp_translated = format_text_for_db(pandas_translator_translate(qn_resp_text))
            text_translations.translated_text = resp_translated
            qn_resp_text = resp_translated
            text_translations.save()
        else:
            qn_resp_text = text_translations.translated_text

        inline_question_response_text, _ = InlineQuestionResponseText.objects.get_or_create(
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

            text_translations, _ = TextTranslations.objects.get_or_create(
                original_text=format_text_for_db(resp_text)
            )
            if not text_translations.translated_text:
                resp_translated = format_text_for_db(pandas_translator_translate(resp_text))
                text_translations.translated_text = resp_translated
                resp_text = resp_translated
                text_translations.save()
            else:
                resp_text = text_translations.translated_text

            inline_question_response_text, _ = InlineQuestionResponseText.objects.get_or_create(
                translated_text=resp_text
            )

            InlineQuestionResponse.objects.create(
                inline_question=created_inline_question, response=inline_question_response_text
            )


def fetch_questions_key_and_name_from_api():
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()   
    url= f"https://staging-api.justgood.work/api/v2/appcontent/query-documents?type=create_content_area&startDate={start_date}&endDate={end_date}"
    response=requests.get(url)
    if response.status_code == 200:
        questions_data=response.json()
        kunfu_panda_logger.info("Successfully fetched questions data from the API")
        filtered_questions = filter_questions_key_and_name_data(questions_data)
        save_filtered_questions_and_keys(filtered_questions)
        translate_inq()
        update_inline_question_text_with_mapper()
        kunfu_panda_logger.info(f" Found {len(filtered_questions)} matches ")
        return filtered_questions  

def update_inline_question_text_with_mapper():
    question_texts = InlineQuestionText.objects.all()
    for question_text in question_texts:
        inqm = InlineQuestionAndKeysMatch.objects.filter(
            inline_question_key = question_text.text
        ).first() 
        if inqm:
            question_text.title_text = inqm.inline_question
            question_text.save()
        
        fq = FollowUpQuestion.objects.filter(
            followup_question_key = question_text.text
        ).first()
        if fq:
            question_text.title_text = fq.followup_question
            question_text.save()


def filter_questions_key_and_name_data(questions_data):
    english_questions = []
    other_languages_questions = []

    for item in questions_data.get('data', []):
        if item.get('language', '').startswith('en'):
            for content in item.get('pageContent', []):
                if content and content.get('type') == 'questions':
                    english_questions.append({**content, **{"custom_lang": "en"}})
        

        else:
            for content in item.get('pageContent', []):
                if content and content.get('type') == 'questions':
                    other_languages_questions.append(content)
            
    return [*english_questions, *other_languages_questions]


def translate_inq():
    inline_questions_key_matches = InlineQuestionAndKeysMatch.objects.filter(custom_lang__isnull=True)
    for inline_questions_key_match in inline_questions_key_matches:
        pandas_translator_inline_question_key_match = pandas_translator_translate(inline_questions_key_match.inline_question)
        inline_questions_key_match.inline_question = pandas_translator_inline_question_key_match
        inline_questions_key_match.custom_lang = 'en'
        inline_questions_key_match.save()

    followup_questions = FollowUpQuestion.objects.filter(custom_lang__isnull=True)
    for followup_question in followup_questions:
        pandas_translator_followup = pandas_translator_translate(followup_question.followup_question)
        followup_question.followup_question = pandas_translator_followup
        followup_question.custom_lang = 'en'
        followup_question.save()


def save_filtered_questions_and_keys(filtered_questions):

    for question_info in filtered_questions:
        question_info_key =  question_info.get("key")
        question_info_text = question_info["question"]
        custom_lang = question_info.get("custom_lang")  

        question_mapper = InlineQuestionAndKeysMatch.objects.filter(
            inline_question_key=question_info_key
            ).first()
        if not question_mapper:
            question_mapper = InlineQuestionAndKeysMatch.objects.create(
                inline_question=question_info_text,
                inline_question_key=question_info_key,
                custom_lang = custom_lang
            )
        
        question_info_options = question_info.get("options")
        for question_info_option in question_info_options:
            option_follow_up_question = question_info_option.get("followUpQuestion")
            if option_follow_up_question:
                follow_up_question_key = option_follow_up_question.get("key")
                follow_up_question_text = option_follow_up_question.get("question")
                fqe = FollowUpQuestion.objects.filter(
                    inline_question__inline_question = question_info_text,
                    followup_question_key = follow_up_question_key
                )
                
                if not fqe:
                    FollowUpQuestion.objects.create(
                        inline_question = question_mapper,
                        followup_question = follow_up_question_text,
                        followup_question_key = follow_up_question_key,
                        custom_lang = custom_lang
                    )

















