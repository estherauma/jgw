import logging

from celery import shared_task

from user_management.cms.partner_configurations import get_partner_configurations

logger = logging.getLogger(__name__)


@shared_task(name="fetch_partner_configurations")
def fetch_partner_configurations():
    logger.info("Fetching organisation partner configurations from Strapi...")
    data = get_partner_configurations()
    if data is None:
        logger.error("Failed to fetch organisation partner configurations from Strapi.")
    else:
        logger.info(
            "Successfully fetched organisation partner configurations from Strapi."
        )
    return data
