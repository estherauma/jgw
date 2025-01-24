from django.db import transaction
from common.services.api_client import JustGoodWorkAPIClient
from preference.models import Preference, OrganisationData
from common.logger import KunfuPandaLogger
from common.const.value_const import org_info_list


def update_preferences_org_code_field():
    """Update preference org_code field with organisationCode from API."""
    kunfu_panda_logger = KunfuPandaLogger()
    jgw_api_client = JustGoodWorkAPIClient()
    update_count = 0

    with transaction.atomic():
        # Get all preferences data from API
        preferences_data = jgw_api_client.get_data("/preferences") or []
        
        for api_preference in preferences_data:
            data_source_id = api_preference.get("_id")
            if not data_source_id:
                continue

            # Find corresponding preference in database
            preference = Preference.objects.filter(data_source_id=data_source_id).first()
            if not preference:
                kunfu_panda_logger.warning(f"No preference found for data_source_id: {data_source_id}")
                continue

            # Get organisationCode from API
            org_code = api_preference.get("organisationCode")
            
            # Update preference org_code field
            preference.org_code = org_code
            preference.save()
            
            update_count += 1
            kunfu_panda_logger.info(
                f"Updated org_code to {org_code} for preference {data_source_id}"
            )

    kunfu_panda_logger.info(f"Updated org_code for {update_count} preferences")
    return update_count
