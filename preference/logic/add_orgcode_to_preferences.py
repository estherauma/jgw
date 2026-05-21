from django.db import transaction
from jgwpandas import settings
from preference.models import OrganisationAccessCode, OrganisationData
from common.logger import KunfuPandaLogger
from user_management.roles import add_default_org_roles
import requests

logger = KunfuPandaLogger(log_file="logs/add_organisation_data.log")

@transaction.atomic
def add_organisation_data_to_db():
    """
    Creates or updates OrganisationData instances based on API response from JustGoodWork API.

    Returns:
        tuple: (created_count, updated_count) - Number of records created and updated
    """
    created_count = 0
    updated_count = 0

    try:
        response = requests.get(
            f"{settings.JGW_API}customcontent-config/v2",
            headers={'secret': settings.JGW_API_SECRET}
        )
        api_data = response.json()

        if isinstance(api_data, dict) and 'data' in api_data:
            for org in api_data['data']:
                try:
                    code = org.get('code')
                    display_name = org.get('displayName')

                    if code and display_name:
                        obj, created = OrganisationData.objects.update_or_create(
                            org_code=code,
                            defaults={"name": display_name}
                        )

                        if created:
                            created_count += 1
                            add_default_org_roles(obj)
                            logger.info(f"Created organization from API: {display_name} with code {code}")
                        else:
                            updated_count += 1
                            logger.info(f"Updated organization from API: {display_name} with code {code}")
                        for access_code_str in org.get('accessCode', []) or []:
                            if access_code_str:
                                OrganisationAccessCode.objects.update_or_create(
                                    code=access_code_str,
                                    defaults={"organisation": obj}
                                )

                except Exception as e:
                    logger.error(f"Error processing API organization {org.get('displayName', 'Unknown')}: {str(e)}")

    except Exception as e:
        logger.error(f"Error fetching data from API: {str(e)}")
        raise e

    return created_count, updated_count
