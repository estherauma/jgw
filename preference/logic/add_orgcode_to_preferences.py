from django.db import transaction
from common.const.value_const import ORGANISATION_DATA
from preference.models import OrganisationData
from common.logger import KunfuPandaLogger

logger = KunfuPandaLogger(log_file="logs/add_organisation_data.log")


@transaction.atomic
def add_organisation_data_to_db():
    """
    Creates or updates OrganisationData instances based on the ORGANISATION_DATA constant.

    Returns:
        tuple: (created_count, updated_count) - Number of records created and updated
    """
    created_count = 0
    updated_count = 0

    for org in ORGANISATION_DATA:
        try:
            obj, created = OrganisationData.objects.update_or_create(
                org_code=org["org_code"], defaults={"name": org["name"]}
            )

            if created:
                created_count += 1
                logger.info(f"Created organization: {org['name']} with code {org['org_code']}")
            else:
                updated_count += 1
                logger.info(f"Updated organization: {org['name']} with code {org['org_code']}")

        except Exception as e:
            logger.error(f"Error processing organization {org['name']}: {str(e)}")
            raise e

    return created_count, updated_count
