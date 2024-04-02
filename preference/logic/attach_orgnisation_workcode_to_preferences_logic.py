from common.const.value_const import NOT_SPECIFIED
from common.helpers.model_helpers.preference import get_or_add_organisation_access_code
from common.logger import KunfuPandaLogger
from common.services.mongodb_manager import MongoDBConnectionManager
from bson.objectid import ObjectId
from preference.models import Preference
from preference.repository.preference_mongo_repo import get_preference_from_mongo_db

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/preference_tasks.log")


def mongodb_pref_by_id(dictionary_list, target_id):
    for item in dictionary_list:
        if item.get("string_id") == target_id:
            return item
    return None


def attach_orgnisation_workcode_to_preferences():
    """
    This retrieves organisation access codes from mongodb database
    and attaches/assign them to preferences in the pandas postgreSQL database.
    """
    preferences_without_accesscode_queryset = Preference.objects.filter(is_missing_accesscode_cleaned=False)
    kunfu_panda_logger.info(
        f"{len(preferences_without_accesscode_queryset)} preferences_without_accesscode_queryset to be updated"
    )

    mongodb_manager = MongoDBConnectionManager()

    BATCH_SIZE = 1000
    added_data_count = 0
    for start in range(0, preferences_without_accesscode_queryset.count(), BATCH_SIZE):
        preferences_batch = preferences_without_accesscode_queryset[start : start + BATCH_SIZE]

        preferences_mongo_ids = [ObjectId(pref.data_source_id) for pref in preferences_batch]
        mongo_preferences_data = get_preference_from_mongo_db(
            mongodb_manager=mongodb_manager,
            preference_mong_ids=preferences_mongo_ids,
            extra_projection_fields={"organisationAccessCode": 1},
        )

        for preference_instance in preferences_batch:
            added_data_count = added_data_count + 1
            data_source_id = preference_instance.data_source_id
            preference_data = mongodb_pref_by_id(mongo_preferences_data, data_source_id)
            preference_instance.is_missing_accesscode_cleaned = True

            if preference_data:
                organisation_access_code_from_mongo = (
                    preference_data.get("organisationAccessCode") or NOT_SPECIFIED
                )

                organisation_access_code_data = get_or_add_organisation_access_code(
                    organisation_access_code_from_mongo
                )

                if preference_data and organisation_access_code_data:
                    preference_instance.organisation_access_code = organisation_access_code_data

            # change is_missing_sector_cleaned property to True to be bulk updated
            preference_instance.save()
    kunfu_panda_logger.info(f"{added_data_count} preferences_without_accesscode_queryset to be updated")
