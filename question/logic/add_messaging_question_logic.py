import os
import requests
from datetime import datetime
from django.conf import settings
from django.db import transaction
from django.db.models import Q, F
from django.db.models.functions import Replace
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.custom_libs.google_translate import pandas_translator_translate
from preference.utils import format_text_for_db
from common.const.localization_const import meassaging_question_response_localization
from common.helpers.model_helpers.preference import (
    get_or_add_country_to_db,
    get_or_add_factory_farm_to_db,
    get_or_add_immigration_status_to_db,
    get_or_add_language_to_db,
    get_or_add_organisation_sector_to_db,
    get_or_add_organisation_to_db,
    get_or_add_route_to_db,
    add_original_sector_of_work_to_db,
)
from common.helpers.preference_helpers.country import get_data_destination, get_data_origin
from common.helpers.preference_helpers.organisation import get_organisation_data
from common.helpers.messaging_question_helpers.messging_question_test_data import is_messaging_question_test_data
from common.logger import KunfuPandaLogger

from common.services.api_client import JustGoodWorkAPIClient, MessagingAPIClient
from common.utils.date_utils import todays_date
from question.logic.update_question_data_with_org_info import update_messaging_question_org_info_from_organisation
from question.models import (
    MessagingQuestion,
    MessagingQuestionResponse,
    MessagingQuestionStandard,
    MessagingQuestionText,
    MessagingResponse,
    MessagingResponseOptionText,
    LeadMessagingQuestionResponse,
    FollowupMessagingQuestionResponse,
    FollowupFollowupMessagingQuestionResponse,
    MessagingQuestionV1,
    MessagingQuestionResponseV1,
    QuestionCategory,
)
from preference.models import Country, FactoryFarm, Gender, ImmigrationStatus, Language, Organisation, OrganisationData, Preference
from question.tasks import translate_and_clean_messaging_question_fields



kunfu_panda_logger = KunfuPandaLogger(log_file="logs/messaging_question_tasks.log")


def fetch_legacy_messaging_question_from_api(client):
    start_date = "2020-11-01"
    end_date = "2022-11-31"

    latest_messaging_question = MessagingQuestionStandard.objects.last()
    if latest_messaging_question:
        start_date = latest_messaging_question.created_at.strftime("%Y-%m-%d")

    return client.get_data(f"/messaging-questions?startDate={start_date}&endDate={end_date}")


def fetch_messaging_question_from_api(client):
    start_date = "2023-11-01"
    end_date = todays_date()

    # get the last time inline question were fetched
    latest_messaging_question = MessagingQuestionStandard.objects.last()
    if latest_messaging_question:
        start_date = latest_messaging_question.created_at.strftime("%Y-%m-%d")

    return client.get_data(f"/question-responses?startDate={start_date}&endDate={end_date}")

def fetch_messaging_question_v3_from_api(jgw_api_client):
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    headers = {"secret": settings.MESSAGING_API_SECRET}

    latest_messaging_question_v3 = MessagingQuestionStandard.objects.last()
    if latest_messaging_question_v3:
        start_date = latest_messaging_question_v3.created_at.strftime("%Y-%m-%d")

    try:
        return jgw_api_client.get_data(f"/question-responses/v2?startDate={start_date}&endDate={end_date}")
    except Exception as e:
        kunfu_panda_logger.error(f"Error fetching messaging questions v3: {str(e)}")
        return []

@transaction.atomic
def fetch_messaging_questions_from_api_to_db():
    messaging_questions = []
    lagacy_jgw_api_client = JustGoodWorkAPIClient()
    jgw_api_client = MessagingAPIClient()

    # legacy
    legacy_messaging_questions_resp = fetch_legacy_messaging_question_from_api(lagacy_jgw_api_client)
    messaging_questions.extend(legacy_messaging_questions_resp)

    # new
    messaging_questions_resp = fetch_messaging_question_from_api(jgw_api_client)
    messaging_questions.extend(messaging_questions_resp)

    # new v3
    try:
        messaging_questions_resp_v3 = fetch_messaging_question_v3_from_api(jgw_api_client)
    except Exception as e:
        kunfu_panda_logger.error(f"Error fetching messaging questions v3: {str(e)}")
        messaging_questions_resp_v3 = []
    
    for messaging_question in messaging_questions:
        try:
            add_messaging_question_to_db(messaging_question)
        except Exception as e:
            print("An error occurred during inline questions creation:", str(e))
            transaction.set_rollback(True)
            raise
    kunfu_panda_logger.info(f"Added {len(messaging_questions)} messaging questions version 1 and 2 to the database")

    for messaging_question in messaging_questions_resp_v3:
        try:
            add_messaging_question_v3_to_db(messaging_question)
        except Exception as e:
            print("An error occurred during messaging questions v3 creation:", str(e))
            transaction.set_rollback(True)
            raise
    kunfu_panda_logger.info(f"Added {len(messaging_questions_resp_v3)} messaging questions v3 to the database")

    # call to translate, question text, response
    translate_and_clean_messaging_question_fields()
    update_translations_from_localization(meassaging_question_response_localization)
    update_myvoice_messaging_questions()
    # update_messaging_question_org_info_from_organisation()


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
    org_code = messaging_question.get("orgCode")
    organisation = messaging_question.get("organisation")
    factory_farm = messaging_question.get("factoryFarm")
    final_sectors_of_work = _final_sectors_of_work_from_payload(messaging_question)

    route_data = get_or_add_route_to_db(route)
    language_data = get_or_add_language_to_db(language)
    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)
    organisation_data = get_or_add_organisation_to_db(organisation)
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)
    is_test_data = is_messaging_question_test_data(messaging_question.get("questionKey"))
    org_data = get_organisation_data(org_code=org_code, organisation=organisation)

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
        is_test_data=is_test_data,
        route=route_data,
        language=language_data,
        origin=origin_data,
        destination=destination_data,
        organisation_sector=organisation_sector_data,
        organisation=organisation_data,
        factory_farm=factory_farm_data,
        org_code=org_code,
        org_info=org_data,
        question_version="V1_and_v2"
    )
    if final_sectors_of_work:
        sectors_of_work_list = add_original_sector_of_work_to_db(final_sectors_of_work)
        messaging_question_standard.sectors_of_work.set(sectors_of_work_list)

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
        for response_option in MessagingResponseOptionText.objects.filter(
            translated_option__contains="&#39;"
        ):
            response_option.translated_option = response_option.translated_option.replace("&#39;", "'")
            response_option.save()
        for entry in localization_data:
            auto_translation = entry["auto_translation"]
            correct_translation = entry["correct_translation"]

            response_option = MessagingResponseOptionText.objects.filter(
                Q(option=auto_translation) | Q(translated_option=auto_translation)
            ).first()

            if response_option:
                response_option.translated_option = correct_translation
                response_option.save()
                print(f"Updated '{auto_translation}' to '{correct_translation}' for id: {response_option.id}")

    except Exception as e:
        print(f"Error during translation update: {str(e)}")


def add_messaging_question_v3_to_db(data):
    try:
        standard_data = {
            'data_source_id': data.get('_id', ''),
            'device_id': data.get('deviceId', ''),
            'app_id': data.get('appId', ''),
            'locale': data.get('locale', ''),
            'org_code': data.get('organisationCode', ''),
            'question_id': data.get('questionKey', ''),
            'is_myvoice_organisation': False,  
            'api_created_at': datetime.fromisoformat(data.get('createdAt').replace('Z', '+00:00')),
            'api_updated_at': datetime.fromisoformat(data.get('updatedAt').replace('Z', '+00:00')),
            'question_version':"V3"
        }

        # preference
        preference = Preference.objects.filter(device_id=data.get('deviceId')).first()
        standard_data['preference'] = preference

        is_test_data = is_messaging_question_test_data(data.get('questionKey'))
        standard_data['is_test_data'] = is_test_data

        if data.get('language'):
            language = Language.objects.filter(code=data.get('language')).first()
            if not language:
                language = Language.objects.create(
                    code=data.get('language'),
                    name=data.get('language')
                )
            standard_data['language'] = language

        if data.get('destination'):
            destination_data = get_or_add_country_to_db(data.get('destination'), source="destination")
            standard_data['destination'] = destination_data

        if data.get('locale'):
            origin = get_or_add_country_to_db(data.get('locale'), source="origin")
            standard_data['origin'] = origin

        organisation = data.get('organisation')
        organisation = get_or_add_organisation_to_db(organisation)
        standard_data['organisation'] = organisation
        org_code = data.get('organisationCode')
        org_data = get_organisation_data(org_code=org_code, organisation=organisation)
        standard_data['org_info'] = org_data

        standard_data['organisation_sector'] = get_or_add_organisation_sector_to_db(
            data.get('organisationSector')
        )

        if data.get('factoryFarm'):
            farm, _ = FactoryFarm.objects.get_or_create(
                name=data.get('factoryFarm')
            )
            standard_data['factory_farm'] = farm

        if data.get('immigrationStatus'):
            status, _ = ImmigrationStatus.objects.get_or_create(
                name=data.get('immigrationStatus')
            )
            standard_data['immigration_status'] = status

        standard, created = MessagingQuestionStandard.objects.update_or_create(
            data_source_id=standard_data['data_source_id'],
            defaults=standard_data
        )

        final_sectors_of_work = _final_sectors_of_work_from_payload(data)
        if final_sectors_of_work:
            sec_of_work_list = add_original_sector_of_work_to_db(final_sectors_of_work)
            standard.sectors_of_work.set(sec_of_work_list)

        question_text, _ = MessagingQuestionText.objects.get_or_create(
            text=data.get('questionText', ''),
            defaults={
                'translated_text': data.get('questionText', '')
            }
        )

        question, _ = MessagingQuestion.objects.update_or_create(
            messaging_question_standard=standard,
            defaults={
                'question': question_text
            }
        )

        response_type = data.get('questionResponseType')
        question_value = data.get('questionValue')

        def _get_or_create_response(option_text, value):
            response = MessagingResponse.objects.filter(
                option=option_text, value=value
            ).first()
            if not response:
                response = MessagingResponse.objects.create(
                    option=option_text, value=value
                )
            return response

        if response_type == 'select' and isinstance(question_value, list):
            for value in question_value:
                option_text, _ = MessagingResponseOptionText.objects.get_or_create(
                    option=value.get('option', ''),
                    defaults={
                        'translated_option': None
                    }
                )
                response = _get_or_create_response(
                    option_text, value.get('key', '')
                )
                question_response, _ = MessagingQuestionResponse.objects.get_or_create(
                    messaging_question=question
                )
                question_response.responses.add(response)

        elif response_type == 'radio' and isinstance(question_value, dict):
            option_text, _ = MessagingResponseOptionText.objects.get_or_create(
                option=question_value.get('option', ''),
                defaults={
                    'translated_option': None
                }
            )
            response = _get_or_create_response(
                option_text, question_value.get('key', '')
            )
            question_response, _ = MessagingQuestionResponse.objects.get_or_create(
                messaging_question=question
            )
            question_response.responses.add(response)

        elif response_type == 'text':
            option_text, _ = MessagingResponseOptionText.objects.get_or_create(
                option=question_value,
                defaults={
                    'translated_option': None
                }
            )
            response = _get_or_create_response(
                option_text, str(question_value)
            )
            question_response, _ = MessagingQuestionResponse.objects.get_or_create(
                messaging_question=question
            )
            question_response.responses.add(response)

        return True

    except Exception as e:
        print(f"Error processing messaging question v3: {str(e)}")
        return False

def _final_sectors_of_work_from_payload(payload):
    sectors_of_work = payload.get("sectorsOfWork")
    sector_of_work_list = payload.get("sectorOfWork")
    sectors = payload.get("sectors")
    final_sectors_of_work = None
    if sector_of_work_list:
        final_sectors_of_work = sector_of_work_list
    if sectors_of_work:
        final_sectors_of_work = sectors_of_work
    if sectors:
        final_sectors_of_work = sectors
    return final_sectors_of_work



def update_myvoice_messaging_questions():
    with transaction.atomic():
        not_specified_org = Organisation.objects.get(name="not specified")
        myvoice_org = Organisation.objects.get(name="myvoice")
        malaysia_country = Country.objects.get(name="malaysia")

        messaging_questions_to_update = MessagingQuestionStandard.objects.filter(
            organisation=not_specified_org, destination=malaysia_country
        )

        updated_count = messaging_questions_to_update.update(
            organisation=myvoice_org, is_myvoice_organisation=True
        )

    return updated_count


def reverse_myvoice_messaging_questions():
    with transaction.atomic():

        not_specified_org = Organisation.objects.get(name="not specified")

        messaging_questions_to_reverse = MessagingQuestionStandard.objects.filter(
            is_myvoice_organisation=True
        )

        updated_count = messaging_questions_to_reverse.update(
            organisation=not_specified_org, is_myvoice_organisation=False
        )

    return updated_count


def translate_and_update_response_text(response_obj, response_text):
    """
    Translates response text to English and updates the response_text_translated field.
    
    Args:
        response_obj: MessagingQuestionResponseV1 or InlineQuestionResponseV1 instance
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


def fetch_messaging_question_v2_from_api(client):
    """
    Fetches messaging questions version 2 from the API.

    This function retrieves messaging questions data from the API, starting from either
    the application's possible start date or the date of the last fetched question,
    up to the current date.

    Args:
        client: An instance of the API client used to make requests.

    Returns:
        A list of messaging questions (version 2) retrieved from the API.
    """
    
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    try:
        latest_messaging_question = (
            LeadMessagingQuestionResponse.objects.order_by("-api_created_at").first()
        )
        if latest_messaging_question:
            start_date = latest_messaging_question.api_created_at.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        kunfu_panda_logger.info(f"Could not query existing records (table may not exist): {str(e)}. Using default start date: {start_date}")

    base_url = settings.MESSAGING_API_BASE_URL
    endpoint = f"/v1/question-responses/v2?startDate={start_date}&endDate={end_date}"
    url = f"{base_url}{endpoint}"
    
    api_secret = getattr(settings, 'MESSAGING_API_SECRET', None) or os.environ.get("JGW_MESSAGING_API_SECRET")
    headers = {"secret": api_secret} if api_secret else {}
    
    kunfu_panda_logger.info(f"Fetching messaging questions v2 from: {url}")
    kunfu_panda_logger.info(f"Date range: {start_date} to {end_date}")
    
    try:
        response = requests.get(url, headers=headers)
        
        kunfu_panda_logger.info(f"API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            kunfu_panda_logger.error(
                f"API returned status {response.status_code}. Response: {response.text[:500]}"
            )
            return []
        
        response_data = response.json()
        kunfu_panda_logger.info(f"API Response type: {type(response_data)}")
        
        if isinstance(response_data, dict):
            if "data" in response_data:
                data = response_data.get("data", [])
                kunfu_panda_logger.info(f"Found 'data' key in response. Length: {len(data) if isinstance(data, list) else 'N/A'}")
                return data if isinstance(data, list) else []
            elif "status" in response_data and response_data.get("status") == "OK":
                data = response_data.get("data", [])
                kunfu_panda_logger.info(f"Found status OK response. Data length: {len(data) if isinstance(data, list) else 'N/A'}")
                return data if isinstance(data, list) else []
            else:
                kunfu_panda_logger.warning(f"Unexpected dict response structure: {list(response_data.keys())}")
                return []
        elif isinstance(response_data, list):
            kunfu_panda_logger.info(f"Response is a list. Length: {len(response_data)}")
            return response_data
        else:
            kunfu_panda_logger.warning(f"Unexpected response type: {type(response_data)}")
            return []
            
    except requests.exceptions.RequestException as e:
        kunfu_panda_logger.error(f"Request exception when fetching messaging questions v2: {str(e)}")
        return []
    except ValueError as e:
        kunfu_panda_logger.error(f"JSON decode error when fetching messaging questions v2: {str(e)}")
        return []
    except Exception as e:
        kunfu_panda_logger.error(f"Unexpected error when fetching messaging questions v2: {str(e)}")
        import traceback
        kunfu_panda_logger.error(traceback.format_exc())
        return []


def store_new_v2_messaging_questions(jgw_api_client):
    """
    Stores v2 messaging questions in the new chain structure.
    Similar to store_new_v3_inline_questions but for messaging questions.
    """
    messaging_questions_v2 = fetch_messaging_question_v2_from_api(jgw_api_client)

    if messaging_questions_v2 is None or not isinstance(messaging_questions_v2, list):
        raise ValueError(
            f"Invalid messaging questions v2 response type: {type(messaging_questions_v2)}"
        )

    if len(messaging_questions_v2) == 0:
        kunfu_panda_logger.info("No new messaging questions v2 received from API (empty list)")
        return 0

    kunfu_panda_logger.info(f"Fetched {len(messaging_questions_v2)} messaging questions v2")

    created_leads = 0
    created_followups = 0
    created_followup_followups = 0

    questions_map = {}
    for question in messaging_questions_v2:
        if isinstance(question, dict):
            device_id = question.get('deviceId')
            if device_id:
                if device_id not in questions_map:
                    questions_map[device_id] = {}
                questions_map[device_id][question.get('questionKey')] = question

    for question in messaging_questions_v2:
        if not isinstance(question, dict):
            continue
        if question.get('isLeadQuestion'):
            try:
                question_value = question.get('questionValue')
                value_key, value_option, followup_key = extract_question_value_data(question_value)

                language_data = get_or_add_language_to_db(question.get("language"))
                destination_data = get_or_add_country_to_db(question.get("destination"), source="destination")
                origin_data = get_or_add_country_to_db(question.get("locale"), source="origin")
                immigration_status_data = get_or_add_immigration_status_to_db(question.get("immigrationStatus"))
                organisation_sector_data = get_or_add_organisation_sector_to_db(question.get("organisationSector"))

                locale_data = get_or_add_country_to_db(question.get("locale"), source="destination")

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
                    kunfu_panda_logger.error(f"Error finding organisation data: {e}")
                    organisation_data = OrganisationData.objects.get(name="Organisation Not Specified")

                device_id = question.get('deviceId')
                preference = Preference.objects.filter(device_id=device_id).first()
                route_data = None
                if preference and preference.route:
                    route_data = preference.route
                else:
                    route_data = get_or_add_route_to_db(None)

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
                
                api_created_at = parse_datetime(question.get('createdAt')) if question.get('createdAt') else timezone.now()
                api_updated_at = parse_datetime(question.get('updatedAt')) if question.get('updatedAt') else timezone.now()

                if LeadMessagingQuestionResponse.objects.filter(data_source_id=question.get("_id")).exists():
                    continue

                messaging_question_v1, _ = MessagingQuestionV1.objects.get_or_create(
                    page_id=question.get('pageId', ''),
                    question_key=question.get('questionKey'),
                    defaults={
                        'page_title': question.get('pageTitle'),
                        'question_text': question.get('questionText'),
                        'question_category': question_category,
                    }
                )

                messaging_question_response_v1, _ = MessagingQuestionResponseV1.objects.get_or_create(
                    response_key=value_key,
                    response_text=value_option,
                    defaults={
                        'response_text_translated': None,
                    }
                )

                if value_option:
                    translate_and_update_response_text(messaging_question_response_v1, value_option)

                lead_response = LeadMessagingQuestionResponse.objects.create(
                    data_source_id=question.get('_id'),
                    device_id=device_id,
                    app_id=question.get('appId'),
                    messaging_question=messaging_question_v1,
                    messaging_question_response=messaging_question_response_v1,
                    response_value=value_key,
                    questionresponsetype=question.get('questionResponseType'),
                    route=route_data,
                    preference=preference,
                    origin=origin_data,
                    destination=destination_data,
                    immigration_status=immigration_status_data,
                    organisation_sector=organisation_sector_data,
                    org_info=organisation_data,
                    language=language_data,
                    locale=locale_data,
                    question_response_date=question_response_date,
                    api_created_at=api_created_at,
                    api_updated_at=api_updated_at,
                )
                created_leads += 1

                if followup_key:
                    followup_question = questions_map.get(device_id, {}).get(followup_key)
                    
                    if followup_question:
                        followup_value = followup_question.get('questionValue')
                        f_value_key, f_value_option, f_followup_key = extract_question_value_data(followup_value)

                        f_question_response_date = None
                        if followup_question.get('questionResponseDate'):
                            f_question_response_date = parse_datetime(followup_question.get('questionResponseDate'))
                        
                        f_api_created_at = parse_datetime(followup_question.get('createdAt')) if followup_question.get('createdAt') else timezone.now()
                        f_api_updated_at = parse_datetime(followup_question.get('updatedAt')) if followup_question.get('updatedAt') else timezone.now()

                        f_question_category = None
                        f_question_categories = followup_question.get('questionCategories', [])
                        if f_question_categories and isinstance(f_question_categories, list) and len(f_question_categories) > 0:
                            f_category_code = f_question_categories[0] if isinstance(f_question_categories[0], str) else f_question_categories[0].get('code')
                            f_category_name = f_question_categories[0] if isinstance(f_question_categories[0], str) else f_question_categories[0].get('name')
                            if f_category_code:
                                f_question_category = QuestionCategory.objects.filter(code=f_category_code).first()
                            elif f_category_name:
                                f_question_category = QuestionCategory.objects.filter(name=f_category_name).first()

                        if FollowupMessagingQuestionResponse.objects.filter(
                            lead_question=lead_response,
                            data_source_id=followup_question.get("_id")
                        ).exists():
                            followup_response = FollowupMessagingQuestionResponse.objects.filter(
                                lead_question=lead_response,
                                data_source_id=followup_question.get("_id")
                            ).first()
                        else:
                            f_messaging_question_v1, _ = MessagingQuestionV1.objects.get_or_create(
                                page_id=followup_question.get('pageId', ''),
                                question_key=followup_question.get('questionKey'),
                                defaults={
                                    'page_title': followup_question.get('pageTitle'),
                                    'question_text': followup_question.get('questionText'),
                                    'question_category': f_question_category,
                                }
                            )

                            f_messaging_question_response_v1, _ = MessagingQuestionResponseV1.objects.get_or_create(
                                response_key=f_value_key,
                                response_text=f_value_option,
                                defaults={
                                    'response_text_translated': None,
                                }
                            )

                            if f_value_option:
                                translate_and_update_response_text(f_messaging_question_response_v1, f_value_option)

                            followup_response = FollowupMessagingQuestionResponse.objects.create(
                                lead_question=lead_response,
                                data_source_id=followup_question.get('_id'),
                                device_id=followup_question.get('deviceId'),
                                messaging_question=f_messaging_question_v1,
                                questionresponsetype=followup_question.get('questionResponseType'),
                                messaging_question_response=f_messaging_question_response_v1,
                                response_value=f_value_key,
                                question_response_date=f_question_response_date,
                                api_created_at=f_api_created_at,
                                api_updated_at=f_api_updated_at,
                            )
                            created_followups += 1

                        if f_followup_key:
                            followup_followup_question = questions_map.get(device_id, {}).get(f_followup_key)
                            
                            if followup_followup_question:
                                ff_value = followup_followup_question.get('questionValue')
                                ff_value_key, ff_value_option, _ = extract_question_value_data(ff_value)

                                ff_question_response_date = None
                                if followup_followup_question.get('questionResponseDate'):
                                    ff_question_response_date = parse_datetime(followup_followup_question.get('questionResponseDate'))
                                
                                ff_api_created_at = parse_datetime(followup_followup_question.get('createdAt')) if followup_followup_question.get('createdAt') else timezone.now()
                                ff_api_updated_at = parse_datetime(followup_followup_question.get('updatedAt')) if followup_followup_question.get('updatedAt') else timezone.now()

                                ff_question_category = None
                                ff_question_categories = followup_followup_question.get('questionCategories', [])
                                if ff_question_categories and isinstance(ff_question_categories, list) and len(ff_question_categories) > 0:
                                    ff_category_code = ff_question_categories[0] if isinstance(ff_question_categories[0], str) else ff_question_categories[0].get('code')
                                    ff_category_name = ff_question_categories[0] if isinstance(ff_question_categories[0], str) else ff_question_categories[0].get('name')
                                    if ff_category_code:
                                        ff_question_category = QuestionCategory.objects.filter(code=ff_category_code).first()
                                    elif ff_category_name:
                                        ff_question_category = QuestionCategory.objects.filter(name=ff_category_name).first()

                                if not FollowupFollowupMessagingQuestionResponse.objects.filter(
                                    followup_question=followup_response,
                                    data_source_id=followup_followup_question.get("_id")
                                ).exists():
                                    ff_messaging_question_v1, _ = MessagingQuestionV1.objects.get_or_create(
                                        page_id=followup_followup_question.get('pageId', ''),
                                        question_key=followup_followup_question.get('questionKey'),
                                        defaults={
                                            'page_title': followup_followup_question.get('pageTitle'),
                                            'question_text': followup_followup_question.get('questionText'),
                                            'question_category': ff_question_category,
                                        }
                                    )

                                    ff_messaging_question_response_v1, _ = MessagingQuestionResponseV1.objects.get_or_create(
                                        response_key=ff_value_key,
                                        response_text=ff_value_option,
                                        defaults={
                                            'response_text_translated': None,
                                        }
                                    )

                                    if ff_value_option:
                                        translate_and_update_response_text(ff_messaging_question_response_v1, ff_value_option)

                                    FollowupFollowupMessagingQuestionResponse.objects.create(
                                        followup_question=followup_response,
                                        data_source_id=followup_followup_question.get('_id'),
                                        device_id=followup_followup_question.get('deviceId'),
                                        messaging_question=ff_messaging_question_v1,
                                        messaging_question_response=ff_messaging_question_response_v1,
                                        response_value=ff_value_key,
                                        questionresponsetype=followup_followup_question.get('questionResponseType'),
                                        question_response_date=ff_question_response_date,
                                        api_created_at=ff_api_created_at,
                                        api_updated_at=ff_api_updated_at,
                                    )
                                    created_followup_followups += 1

            except Exception as e:
                kunfu_panda_logger.error(f"Error processing messaging question {question.get('_id')}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

    kunfu_panda_logger.info(
        "Finished storing new v2 messaging questions. "
        f"leads={created_leads}, followups={created_followups}, followup_followups={created_followup_followups}"
    )

    return created_leads + created_followups + created_followup_followups
