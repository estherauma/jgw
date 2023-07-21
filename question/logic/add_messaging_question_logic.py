from django.db import transaction
from common.const.value_const import NOT_SPECIFIED

from common.services.api_client import JustGoodWorkAPIClient
from common.utils.preferences import get_origin_and_destination_from_route
from question.models import MessagingQuestion, MessagingQuestionOptionResponseAnswer, MessagingQuestionResponse, MessagingQuestionStandard
from preference.models import Preference


def fetch_messaging_question_from_api(client, start_date='2020-01-01', end_date='2023-06-26'):
    return client.get_data(f"/messaging-questions?startDate={start_date}&endDate={end_date}")


        
@transaction.atomic
def fetch_messaging_questions_from_api_to_db():
    
    jgw_api_client = JustGoodWorkAPIClient()
    messaging_questions = fetch_messaging_question_from_api(jgw_api_client)
    
    for messaging_question in messaging_questions:
        try:
            add_messaging_question_to_db(messaging_question)
        except Exception as e:
            print('An error occurred during inline questions creation:', str(e))
            transaction.set_rollback(True)
            raise
 
       
def add_messaging_question_to_db(messaging_question):
    
        route = messaging_question.get('route')
        origin= get_origin_and_destination_from_route(route).get('origin')
        destination= get_origin_and_destination_from_route(route).get('destination')
        
        # save the standard fields, 
        device_id = messaging_question.get('deviceId')
        preference = Preference.objects.filter(device_id=device_id).first()
        
        
        messaging_question_standard = MessagingQuestionStandard.objects.create(
            data_source_id = messaging_question.get('_id'),
            device_id = messaging_question.get('deviceId'),
            preference = preference,
            app_id = messaging_question.get('appId'),
            locale = messaging_question.get('locale'),
            route = route,
            created_at = messaging_question.get('createdAt'),
            api_updated_at = messaging_question.get('updatedAt'),
            api_message_id = messaging_question.get('messageId'),
            question_id = messaging_question.get('questionId')
        )
        
        #  create messaging question text
        messaging_question_text = messaging_question.get('questionText')
        if  messaging_question_text is not None and len(messaging_question_text) > 0:
            messaging_question_text = messaging_question_text[0]
        
        new_messaging_question = MessagingQuestion.objects.create(
            question = messaging_question_text,
            messaging_question_standard = messaging_question_standard
        )
        
        question_responses = messaging_question.get('questionResponse')
        question_response_data_type = type(question_responses)
        
        if question_response_data_type is str:
            # add response as response_text, response_option_type='text' by default
            MessagingQuestionResponse.objects.create(
                messaging_question = new_messaging_question,
                response_text = question_responses
            )

        if question_response_data_type is list:
            new_messaging_question_response = MessagingQuestionResponse.objects.create(
                messaging_question = new_messaging_question,
                response_option_type = "multiple"
            )
            for response_option in question_responses:
                MessagingQuestionOptionResponseAnswer.objects.create(
                    messaging_question_response = new_messaging_question_response,
                    option = response_option.get('value'),
                    answer = response_option.get('isChecked')
                )