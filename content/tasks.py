import logging

from celery import shared_task

from content.services.partner_configurations import sync_partner_configurations

logger = logging.getLogger(__name__)


@shared_task(name="sync_partner_configurations")
def sync_partner_configurations_task():
    logger.info("Syncing partner configurations from Strapi...")
    summary = sync_partner_configurations()
    if summary is None:
        logger.error("Failed to fetch partner configurations from Strapi.")
    else:
        logger.info(
            "Successfully synced partner configurations from Strapi. Sync summary: %s",
            summary,
        )
    return summary

