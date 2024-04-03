from celery import shared_task
from common.custom_libs.google_translate import pandas_translator_translate
from common.helpers.preference_helpers.age import normalize_age
from common.helpers.preference_helpers.gender import normalize_gender_name
from common.helpers.preference_helpers.language import non_translatable_languages
from common.logger import KunfuPandaLogger
from common.services.api_client import JustGoodWorkAPIClient
from preference.logic.attach_orgnisation_accesscode_to_preferences_logic import (
    attach_orgnisation_accesscode_to_preferences,
)
from preference.logic.attach_sectors_to_preferences_logic import (
    attach_sectors_to_preferences,
    clean_sectors_of_work,
    stringified_sectors_of_work_to_list,
)
from preference.models import Age, Country, CountryState, Gender, Language, SectorOfWork

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
        transformed_name = language.name
        if language.name.lower() not in non_translatable_languages():
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


def translate_and_clean_age():
    untransalted_ages = Age.objects.filter(translated_range__isnull=True)
    for age in untransalted_ages:
        tranlated_range = pandas_translator_translate(age.range)
        transformed_range = normalize_age(tranlated_range)
        age.translated_range = transformed_range
        age.save()

    kunfu_panda_logger.info(f"{len(untransalted_ages)} age(s) translated")


def attach_countries_to_state():
    jgw_api_client = JustGoodWorkAPIClient()
    app_config = jgw_api_client.get_data(f"/appconfig/app_config_v3/vanilla?encrypted=false")
    destinations = app_config.get("destinations")

    for destination in destinations:
        country_name = destination.get("countryName").lower()
        country_states = destination.get("states")

        if country_states and len(country_states) > 0:
            country_db_obj = Country.objects.filter(name=country_name).first()
            if not country_db_obj:
                return None

            for country_state in country_states:
                state_db_obj = CountryState.objects.filter(
                    name__iexact=country_state.get("key"), country=None
                ).first()
                if not state_db_obj:
                    return None

                state_db_obj.country = country_db_obj
                if state_db_obj.full_name is None:
                    state_db_obj.full_name = country_state.get("defaultName")
                state_db_obj.save()


def translate_and_clean_preferences_fields(key: str = None):
    translate_and_clean_gender()
    translate_and_clean_language()
    translate_and_clean_sectors_of_work()
    translate_and_clean_age()

    # clean up sectors of work
    attach_sectors_to_preferences()  # may get untranslated sectors of work from db around here
    translate_and_clean_sectors_of_work()  # translate

    stringified_sectors_of_work_to_list()
    translate_and_clean_sectors_of_work()  # translate

    clean_sectors_of_work()

    attach_orgnisation_accesscode_to_preferences()
