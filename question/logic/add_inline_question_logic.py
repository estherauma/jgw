from django.db import transaction
from common.const.value_const import NOT_SPECIFIED

from common.services.api_client import JustGoodWorkAPIClient
from question.models import InlineQuestion, InlineQuestionResponse, InlineQuestionStandard
from preference.models import Preference


def fetch_inline_question_from_api(client):
    return client.get_data("/inlinequestions")


list_fields = ['language', 'locale', 'deviceId', 'createdAt', 'updatedAt', '_id', 'appId', 'route', 'organisation', 'factoryFarm', '__v']
def separate_inline_question_standard_fields_from_others(inline_question_dict):
    other_fields = []
    standard_fields = {}

    for obj_key, obj_value in inline_question_dict.items():
        if obj_key in list_fields:
            standard_fields[obj_key] = obj_value
        if obj_key not in list_fields:
            other_fields.append({"key":obj_key, "value": obj_value})
    
    return {"other_fields_list": other_fields, "standard_fields_dict": standard_fields}

        
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
    if type(inline_question) is not str:
        standard_and_other_fields = separate_inline_question_standard_fields_from_others(inline_question)
        standard_fields_dict = standard_and_other_fields.get("standard_fields_dict")
        other_fields_list = standard_and_other_fields.get("other_fields_list")
        
        # delete all from models
        # InlineQuestionStandard.objects.all().delete()
        # InlineQuestion.objects.all().delete()
        # InlineQuestionResponse.objects.all().delete()
        
        # save the standard fields, 
        inline_question_standard = InlineQuestionStandard.objects.create(
            data_source_id = standard_fields_dict.get('_id'),
            device_id = standard_fields_dict.get('deviceId'),
            app_id = standard_fields_dict.get('appId'),
            locale = standard_fields_dict.get('locale'),
            route = standard_fields_dict.get('route'),
            language = standard_fields_dict.get('language'),
            organisation = standard_fields_dict.get('organisation'),
            organisation_sector = standard_fields_dict.get('organisationSector'),
            factory_farm = standard_fields_dict.get('factoryFarm'),
            created_at = standard_fields_dict.get('createdAt'),
            updated_at = standard_fields_dict.get('updatedAt')
        )
        
        #  save inline question with standard ID
        for other_field in other_fields_list:
            inline_question = InlineQuestion.objects.filter(
                question = other_field.get('key')
            ).first()
            
            if not inline_question:
                inline_question = InlineQuestion.objects.create(
                    inline_question_standard = inline_question_standard,
                    question = other_field.get('key')
                )
            
            InlineQuestionResponse.objects.create(
                inline_question = inline_question,
                response = other_field.get('value')
            )