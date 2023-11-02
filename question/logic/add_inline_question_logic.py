from django.db import transaction
import re
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.custom_libs.google_translate import pandas_translator_translate
from common.helpers.model_helpers.preference import get_or_add_country_to_db, get_or_add_factory_farm_to_db, get_or_add_language_to_db, get_or_add_organisation_sector_to_db, get_or_add_organisation_to_db, get_or_add_route_to_db
from common.logger import KunfuPandaLogger

from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date
from common.helpers.preference_helpers.country import get_origin_and_destination_from_route
from preference.utils import format_text_for_db
from question.models import InlineQuestion, InlineQuestionResponse, InlineQuestionResponseText, InlineQuestionStandard, InlineQuestionText
from preference.models import Preference, TextTranslations
from question.tasks import translate_and_clean_inline_question_fields


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/inline_question_tasks.log")

def fetch_inline_question_from_api(client):
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()
    
    # get the last time inline question were fetched
    latest_inlinequestion = InlineQuestionStandard.objects.last()
    if latest_inlinequestion:
        start_date = latest_inlinequestion.created_at.strftime("%Y-%m-%d")
        
    kunfu_panda_logger.info(f"Fetching inline questions from {start_date} to {end_date}")
    return client.get_data(f"/inlinequestions?startDate={start_date}&endDate={end_date}")


unwanted_fields = ['_id',
 'deviceId',
 'appId',
 'locale',
 'route',
 'organisation',
 'organisationSector',
 'factoryFarm',
 'createdAt',
 'updatedAt',
 '__v',
 'age',
 'appVersion',
 'deviceModel',
 'os',
 'osVersion',
 'questionKey',
 'questionSection',
 'questionText',
 'questionValue',
 'sectors',
 'seenTabWelcomeText',
 'destinationRepository',
 'destination',
 'destinationState',
 'gender',
 'language'
]

def separate_inline_question_standard_fields_from_others(inline_question_dict):
    other_fields = []
    standard_fields = {}

    for obj_key, obj_value in inline_question_dict.items():
        if obj_key in unwanted_fields:
            standard_fields[obj_key] = obj_value
        if obj_key not in unwanted_fields:
            other_fields.append({"key":obj_key, "value": obj_value})
    
    return {"responses_list": other_fields, "standard_fields_dict": standard_fields}

def format_inline_question_response_text(text):
    inline_question_text = text
    if isinstance(text, str):
        if text == 'undefined' or text == '' or text == ' ' or text is None:
            inline_question_text = NOT_SPECIFIED

        cleaned_text = re.sub(r'<br/>', '', inline_question_text)
        return cleaned_text
    return text

        
@transaction.atomic
def fetch_inline_questions_from_api_to_db():
    
    jgw_api_client = JustGoodWorkAPIClient()
    inline_questions = fetch_inline_question_from_api(jgw_api_client)
    
    for inline_question in inline_questions:
        try:
            add_inline_question_to_db(inline_question)
        except Exception as e:
            print('An error occurred during inline questions creation:', str(e))
            transaction.set_rollback(True)
            raise
    kunfu_panda_logger.info(f'Added {len(inline_questions)} inline questions to the database')
    
    translate_and_clean_inline_question_fields()
       
def add_inline_question_to_db(inline_question):
     
    if isinstance(inline_question, str):
        return
    
    standard_and_other_fields = separate_inline_question_standard_fields_from_others(inline_question)
    
    if InlineQuestionStandard.objects.filter(data_source_id=inline_question.get("_id")).exists():
        return
        
        
    standard_fields_dict = standard_and_other_fields.get("standard_fields_dict")
    responses_list = standard_and_other_fields.get("responses_list")
    
    route = standard_fields_dict.get('route') or NOT_SPECIFIED
    origin= get_origin_and_destination_from_route(route).get('origin')
    destination= get_origin_and_destination_from_route(route).get('destination')
    language = standard_fields_dict.get('language')
    organisation_sector = standard_fields_dict.get('organisationSector')
    organisation = standard_fields_dict.get('organisation')
    factory_farm = standard_fields_dict.get('factoryFarm')
    
    route_data = get_or_add_route_to_db(route)
    language_data = get_or_add_language_to_db(language)
    origin_data = get_or_add_country_to_db(origin, source="origin")
    destination_data = get_or_add_country_to_db(destination, source="destination")
    organisation_sector_data = get_or_add_organisation_sector_to_db(organisation_sector)
    organisation_data = get_or_add_organisation_to_db(organisation)
    factory_farm_data = get_or_add_factory_farm_to_db(factory_farm)
    
    # save the standard fields, 
    device_id = standard_fields_dict.get('deviceId')
    preference = Preference.objects.filter(device_id=device_id).first()
    
    inline_question_standard = InlineQuestionStandard.objects.create(
        data_source_id = standard_fields_dict.get('_id'),
        device_id = device_id,
        preference = preference,
        app_id = standard_fields_dict.get('appId'),
        locale = standard_fields_dict.get('locale'),
        route = route_data,
        language = language_data,
        origin = origin_data,
        destination = destination_data,
        organisation_sector = organisation_sector_data,
        organisation = organisation_data,
        factory_farm = factory_farm_data,
        api_created_at = standard_fields_dict.get('createdAt'),
        api_updated_at = standard_fields_dict.get('updatedAt')
    )
    
    #  get or create inline question text
    if 'questionKey' in inline_question:
        inline_question_text, _ = InlineQuestionText.objects.get_or_create(
            text = format_inline_question_response_text(inline_question.get('questionKey')),
        )
        inline_question_text.title_text = inline_question.get('questionText')
        inline_question_text.save()
        
        created_inline_question = InlineQuestion.objects.create(
            question = inline_question_text,
            inline_question_standard = inline_question_standard
        )
        
        # create inline question response 
        qn_resp_text = format_inline_question_response_text(inline_question.get('questionValue')) or NOT_SPECIFIED
        if isinstance(qn_resp_text, dict) and "amount" in qn_resp_text:
            qn_resp_text = qn_resp_text.get("amount")
        
        text_translations, _ = TextTranslations.objects.get_or_create(original_text=format_text_for_db(qn_resp_text))
        if not text_translations.translated_text:
            resp_translated = format_text_for_db(pandas_translator_translate(qn_resp_text))
            text_translations.translated_text = resp_translated
            qn_resp_text = resp_translated
            text_translations.save()
        else:
            qn_resp_text = text_translations.translated_text
                
        inline_question_response_text, _ = InlineQuestionResponseText.objects.get_or_create(
            translated_text = qn_resp_text
        )
            
        inline_question_text.title_text = inline_question.get('questionText')
        inline_question_text.save()
        
        InlineQuestionResponse.objects.create(
            inline_question = created_inline_question,
            response = inline_question_response_text
        )
    else:
        for response_list in responses_list:
            inline_question_text, _ = InlineQuestionText.objects.get_or_create(
                text = format_inline_question_response_text(response_list.get('key'))
            )
            
            created_inline_question = InlineQuestion.objects.create(
                question = inline_question_text,
                inline_question_standard = inline_question_standard
            )
            
            # create inline question response 
            resp_text = format_inline_question_response_text(response_list.get('value')) or NOT_SPECIFIED
            if isinstance(resp_text, dict) and "amount" in resp_text:
                resp_text = resp_text.get("amount") 
            
            
            text_translations, _ = TextTranslations.objects.get_or_create(original_text=format_text_for_db(resp_text))
            if not text_translations.translated_text:
                resp_translated = format_text_for_db(pandas_translator_translate(resp_text))
                text_translations.translated_text = resp_translated
                resp_text = resp_translated
                text_translations.save()
            else:
                resp_text = text_translations.translated_text
                
            inline_question_response_text, _ = InlineQuestionResponseText.objects.get_or_create(
                translated_text = resp_text
            )
                
                
            InlineQuestionResponse.objects.create(
                inline_question = created_inline_question,
                response = inline_question_response_text
            )