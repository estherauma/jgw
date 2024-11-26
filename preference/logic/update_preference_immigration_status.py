from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from django.db import transaction
from common.helpers.model_helpers.preference import get_or_add_immigration_status_to_db
from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date
from preference.models import Preference
from common.logger import KunfuPandaLogger

kunfu_panda_logger = KunfuPandaLogger(log_file="logs/preference_tasks.log")


@transaction.atomic
def update_preferences_immigration_status():
    jgw_api_client = JustGoodWorkAPIClient()
    start_date = APPLICATION_POSSIBLE_START_DATE
    end_date = todays_date()

    preferences = jgw_api_client.get_data(f"/preferences?startDate={start_date}&endDate={end_date}") or []

    update_count = 0
    for preference in preferences:
        api_id = preference.get("_id")
        immigration_status = preference.get("immigrationStatus")
        immigration_status_instance = get_or_add_immigration_status_to_db(immigration_status)

        if not immigration_status_instance:
            continue
        updated = Preference.objects.filter(data_source_id=api_id).update(
            immigration_status=immigration_status_instance
        )
        update_count += updated

    kunfu_panda_logger.info(f"Updated immigration status for {update_count} preferences")
    return update_count
