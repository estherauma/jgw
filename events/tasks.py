from celery import shared_task
from common.custom_libs.google_translate import pandas_translator_translate
from common.logger import KunfuPandaLogger

from events.models import ChaptersFeedbackResponse


kunfu_panda_logger = KunfuPandaLogger(log_file="logs/events_chapter_tasks.log")

def translate_and_clean_chapter_feedback_fields():
    chapters_feedback_response = ChaptersFeedbackResponse.objects.filter(translated_response__isnull=True)
    
    for chapters_feedback in chapters_feedback_response:
        transformed_name = pandas_translator_translate(chapters_feedback.response)
        chapters_feedback.translated_response = transformed_name
        chapters_feedback.save()
    
    kunfu_panda_logger.info(f"{len(chapters_feedback_response)} chapters feedback responses translated")