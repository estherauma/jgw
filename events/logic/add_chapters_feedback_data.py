from django.db import transaction
from common.const.value_const import APPLICATION_POSSIBLE_START_DATE, NOT_SPECIFIED
from common.helpers.model_helpers.preference import get_or_add_country_to_db, get_or_add_factory_farm_to_db, get_or_add_language_to_db, get_or_add_organisation_sector_to_db, get_or_add_organisation_to_db, get_or_add_route_to_db
from common.logger import KunfuPandaLogger

from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date
from common.helpers.preference_helpers.country import get_origin_and_destination_from_route
from events.models import ChaptersFeedback
from preference.models import Preference
from question.tasks import translate_and_clean_inline_question_fields


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/hapters_feedback_tasks.log")

def fetch_chapters_feedback_from_api(client):
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()
    
    # get the last time inline question were fetched
    latest_chapters_feedback = ChaptersFeedback.objects.last()
    if latest_chapters_feedback:
        start_date = latest_chapters_feedback.created_at.strftime("%Y-%m-%d")
        
    kunfu_panda_logger.info(f"Fetching chapters feedback from {start_date} to {end_date}")
        
    return client.get_data(f"/inlinequestions?startDate={start_date}&endDate={end_date}")

        
@transaction.atomic
def fetch_chapters_feedback_from_api_to_db():
    
    jgw_api_client = JustGoodWorkAPIClient()
    chapters_feedback = fetch_chapters_feedback_from_api(jgw_api_client)
    
    for chapter_feedback in chapters_feedback:
        try:
            add_chapter_feedback_to_db(chapter_feedback)
        except Exception as e:
            print('An error occurred during inline questions creation:', str(e))
            transaction.set_rollback(True)
            raise
    kunfu_panda_logger.info(f'Added {len(chapters_feedback)} chapters feedback to the database')
    
    translate_and_clean_inline_question_fields()
       
def add_chapter_feedback_to_db(inline_question):
    print(inline_question)