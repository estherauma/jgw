from django.db import transaction
from common.const.value_const import NOT_SPECIFIED

from common.services.api_client import JustGoodWorkAPIClient
from question.models import InlineQuestion
from preference.models import Preference


def fetch_inline_question_from_api(client):
    return client.get_data("/inlinequestions")

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
    # get preference from db by device_id
    preference = Preference.objects.get(device_id=inline_question.get('deviceId'))