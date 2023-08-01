from celery import shared_task
from common.custom_libs.google_translate import pandas_translator_translate
from common.helpers.preference_helpers.gender import normalize_gender_name
from common.logger import KunfuPandaLogger
from preference.models import Gender, Language, SectorOfWork

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/preference_tasks.log")


def translate_and_clean_gender():
    untransalted_genders = Gender.objects.filter(translated_name__isnull=True)
    for gender in untransalted_genders:
        translated_name = pandas_translator_translate(gender.name)
        transformed_name = normalize_gender_name(translated_name.lower())
        gender.translated_name = transformed_name
        gender.save()
    
    kunfu_panda_logger.info(f"{len(untransalted_genders)} gender(s) translated")
    

def translate_and_clean_language():
    untransalted_languages = Language.objects.filter(translated_name__isnull=True)
    for language in untransalted_languages:
        transformed_name = pandas_translator_translate(language.name)
        translated_name = transformed_name 
        language.translated_name = translated_name.lower()
        
        language.save()
        
    kunfu_panda_logger.info(f"{len(untransalted_languages)} language(s) translated")


def translate_and_clean_sectors_of_work():
    untranslated_sectors_of_work = SectorOfWork.objects.filter(translated_name__isnull=True)
    for sector_work in untranslated_sectors_of_work:
        transformed_name = pandas_translator_translate(sector_work.name)
        sector_work.translated_name = transformed_name
        sector_work.save()
    
    kunfu_panda_logger.info(f"{len(untranslated_sectors_of_work)} sector(s) of work translated")
    
    
# @shared_task(name="translate_preferences_field")    
def translate_and_clean_preferences_fields():
    translate_and_clean_gender()
    translate_and_clean_language()
    translate_and_clean_sectors_of_work()
    