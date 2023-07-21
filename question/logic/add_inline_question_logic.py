from django.db import transaction
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.helpers.model_helpers.preference import get_or_add_country_to_db, get_or_add_factory_farm_to_db, get_or_add_language_to_db, get_or_add_organisation_sector_to_db, get_or_add_organisation_to_db, get_or_add_route_to_db

from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date
from common.utils.preferences import get_origin_and_destination_from_route
from question.models import InlineQuestion, InlineQuestionResponse, InlineQuestionStandard, InlineQuestionText
from preference.models import Preference


def fetch_inline_question_from_api(client):
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()
    
    # get the last time inline question were fetched
    latest_inlinequestion = InlineQuestionStandard.objects.last()
    if latest_inlinequestion:
        start_date = latest_inlinequestion.created_at.strftime("%Y-%m-%d")
        
    print(f"Fetching inline questions from {start_date} to {end_date}")
        
    return client.get_data(f"/inlinequestions?startDate={start_date}&endDate={end_date}")


list_fields = ['language', 'locale', 'deviceId', 'createdAt', 'updatedAt', '_id', 'appId', 'route', 'organisation', 'factoryFarm', '__v']
def separate_inline_question_standard_fields_from_others(inline_question_dict):
    other_fields = []
    standard_fields = {}

    for obj_key, obj_value in inline_question_dict.items():
        if obj_key in list_fields:
            standard_fields[obj_key] = obj_value
        if obj_key not in list_fields:
            other_fields.append({"key":obj_key, "value": obj_value})
    
    return {"responses_list": other_fields, "standard_fields_dict": standard_fields}

        
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
    origin_data = get_or_add_country_to_db(origin, "origin_data")
    destination_data = get_or_add_country_to_db(destination, "destination_data")
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
    for response_list in responses_list:
        inline_question_text, _ = InlineQuestionText.objects.get_or_create(
            text = response_list.get('key'),
        )
        
        inline_question = InlineQuestion.objects.create(
            question = inline_question_text,
            inline_question_standard = inline_question_standard
        )
        
        # create inline question response 
        InlineQuestionResponse.objects.create(
            inline_question = inline_question,
            response = response_list.get('value')
        )