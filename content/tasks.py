import logging

from celery import shared_task

from content.services.partner_configurations import (
    sync_partner_config_options,
)

logger = logging.getLogger(__name__)


@shared_task(name="sync_partner_config_options")
def sync_partner_config_options_task():
    logger.info("Syncing partner configuration options from Strapi...")
    summary = sync_partner_config_options()
    if summary is None:
        logger.error("Failed to fetch partner configuration options from Strapi.")
    else:
        logger.info(
            "Successfully synced partner configuration options from Strapi. Sync summary: %s",
            summary,
        )
    return summary
