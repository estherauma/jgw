import pandas as pd
from django.db.models.functions import Length
from bson.objectid import ObjectId

from common.helpers.model_helpers.preference import add_sector_of_work_to_db
from common.services.mongodb_manager import MongoDBConnectionManager
from preference.models import Preference, SectorOfWork
from preference.repository.preference_mongo_repo import get_preference_from_mongo_db


def find_by_id(dictionary_list, target_id):
    for item in dictionary_list:
        if item.get("string_id") == target_id:
            return item
    return None


def attach_sectors_to_preferences():
    """
    This retrieves sectors of work from mongodb database
    and attaches/assign them to preferences in the pandas postgreSQL database.
    """
    preferences_without_sectors_of_work_queryset = Preference.objects.filter(
        sectors_of_work__translated_name="not specified", is_missing_sector_cleaned=False
    )

    mongodb_manager = MongoDBConnectionManager()

    BATCH_SIZE = 1000
    for start in range(0, preferences_without_sectors_of_work_queryset.count(), BATCH_SIZE):
        preferences_batch = preferences_without_sectors_of_work_queryset[start : start + BATCH_SIZE]

        preferences_mongo_ids = [ObjectId(pref.data_source_id) for pref in preferences_batch]
        mongo_preferences_data = get_preference_from_mongo_db(
            mongodb_manager=mongodb_manager, preference_mong_ids=preferences_mongo_ids
        )

        for preference_instance in preferences_batch:
            data_source_id = preference_instance.data_source_id
            preference_data = find_by_id(mongo_preferences_data, data_source_id)

            if preference_data:
                preference_instance.sectors_of_work.clear()
                sec_of_work_list = add_sector_of_work_to_db(preference_data["final_sectors_of_work"])
                for sec_of_work in sec_of_work_list:
                    preference_instance.sectors_of_work.add(sec_of_work)

            # change is_missing_sector_cleaned property to True to be bulk updated
            preference_instance.is_missing_sector_cleaned = True

        # bulk update
        Preference.objects.bulk_update(preferences_batch, ["is_missing_sector_cleaned"])


def stringified_sectors_of_work_to_list():
    preference_instances = Preference.objects.annotate(
        name_length=Length("sectors_of_work__translated_name")
    ).filter(name_length__lt=2)

    mongodb_manager = MongoDBConnectionManager()
    preferences_mongo_ids = [ObjectId(pref.data_source_id) for pref in preference_instances]
    mongo_preferences_data = get_preference_from_mongo_db(
        mongodb_manager=mongodb_manager, preference_mong_ids=preferences_mongo_ids
    )

    for preference in preference_instances:
        preference.sectors_of_work.clear()

        data_source_id = preference.data_source_id
        preference_from_mongo_db = find_by_id(mongo_preferences_data, data_source_id)
        if preference_from_mongo_db:
            sec_of_work_list = add_sector_of_work_to_db(preference_from_mongo_db["final_sectors_of_work"])
            for sec_of_work in sec_of_work_list:
                preference.sectors_of_work.add(sec_of_work)

    SectorOfWork.objects.annotate(name_length=Length("name")).filter(name_length__lt=2).delete()


def clean_sectors_of_work():
    sectors_of_work = SectorOfWork.objects.all()
    for sector_of_work in sectors_of_work:
        cleaned_name = (
            sector_of_work.name
            if sector_of_work and not sector_of_work.translated_name
            else sector_of_work.translated_name
        )
        sector_of_work.translated_name = (
            cleaned_name.strip().lower().replace("&amp;", "and").replace("&", "and")
        )

        sector_of_work.save()


def export_sectors_of_work_to_excel():
    sectors_of_work = SectorOfWork.objects.all()
    sectors_of_work_list = [
        {
            "name": sec.name,
            "translated_name": sec.translated_name,
        }
        for sec in sectors_of_work
    ]
    df = pd.DataFrame(sectors_of_work_list)
    df.to_excel("sectors_of_work.xlsx", index=False)
