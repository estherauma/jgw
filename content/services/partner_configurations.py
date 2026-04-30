import json
import logging
import re

import requests
from django.conf import settings
from django.db import transaction

from content.models import Collection, Locale, WorkSector
from preference.models import OrganisationAccessCode, OrganisationData, SiteLanguages
from content.services.utils import get_cms_headers, get_cms_session
from user_management.roles import add_default_org_roles

logger = logging.getLogger(__name__)


def _extract_language_values(collection_languages):
    values = []
    if not isinstance(collection_languages, list):
        return values

    for item in collection_languages:
        if not isinstance(item, dict):
            continue
        children = item.get("children", [])
        if not isinstance(children, list):
            continue
        for child in children:
            if not isinstance(child, dict):
                continue
            text = (child.get("text") or "").strip()
            if text:
                values.append(text)
    return values


def _parse_language_value(value):
    if "(" in value and value.endswith(")"):
        code, language_name = value.split("(", 1)
        return code.strip(), language_name[:-1].strip()
    return value.strip(), None


def sync_organisation_languages(organisation, collection_languages):
    language_values = _extract_language_values(collection_languages)
    parsed_languages = []
    for value in language_values:
        code, language_name = _parse_language_value(value)
        if not code:
            continue
        parsed_languages.append((code, language_name))

    SiteLanguages.objects.filter(organisation=organisation).delete()

    for code, language_name in parsed_languages:
        SiteLanguages.objects.create(
            organisation=organisation,
            code=code,
            name=language_name,
        )

    return len(parsed_languages)


def sync_partner_configuration_item(item):
    org_code = (item.get("org_code") or "").strip()
    name = (item.get("display_name") or (item.get("name") or "")).strip()

    if not org_code or not name:
        logger.warning(
            "Skipping partner configuration with missing org_code or name: %s",
            item,
        )
        return {"created": 0, "updated": 0, "languages_created": 0}

    defaults = {
        "name": name,
        "custom_type": item.get("custom_type"),
        "work_sector": item.get("work_sector"),
        "content_collection": item.get("content_collection"),
        "default_collection_language": item.get("default_collection_language"),
    }

    with transaction.atomic():
        organisation, created = OrganisationData.objects.update_or_create(
            org_code=org_code,
            defaults=defaults,
        )

        if created:
            add_default_org_roles(organisation)

        languages_created = sync_organisation_languages(
            organisation=organisation,
            collection_languages=item.get("collection_languages"),
        )

        access_codes_raw = (item.get("access_code") or "").strip()
        access_codes = [
            code.strip() for code in access_codes_raw.split(",") if code and code.strip()
        ]
        for code in access_codes:
            OrganisationAccessCode.objects.update_or_create(
                code=code,
                defaults={"organisation": organisation},
            )

    return {
        "created": 1 if created else 0,
        "updated": 0 if created else 1,
        "languages_created": languages_created,
    }


def sync_partner_configurations():
    """
    Sync Strapi partner configurations into OrganisationData and SiteLanguages.
    """
    try:
        payload = get_partner_configurations()
        if payload is None:
            return None

        items = payload.get("data", [])

        created_count = 0
        updated_count = 0
        languages_created_count = 0

        for item in items:
            result = sync_partner_configuration_item(item)
            created_count += result["created"]
            updated_count += result["updated"]
            languages_created_count += result["languages_created"]

        return {
            "created": created_count,
            "updated": updated_count,
            "languages_created": languages_created_count,
        }
    except Exception:
        logger.exception("Unexpected error while syncing partner configurations")
        return None


def get_partner_configurations():
    """
    Fetch organisation partner configurations from the CMS.

    Returns the parsed JSON response on success, or None on failure.
    Retries up to 3 times with exponential backoff on connection/timeout errors.
    """
    base_url = settings.STRAPI_API_BASE_URL

    if not base_url or not settings.STRAPI_API_TOKEN:
        logger.error(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )
        return None

    url = f"{base_url.rstrip('/')}/partner-configurations"
    session = get_cms_session()
    headers = get_cms_headers()

    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as exc:
        logger.error(
            "HTTP error fetching partner configurations from CMS: %s", exc
        )
    except requests.exceptions.RequestException as exc:
        logger.error(
            "Error fetching partner configurations from CMS: %s", exc
        )
    return None


def get_partner_configuration_options():
    """
    Fetch partner configuration options from the CMS.

    Endpoint:
      /partner-configurations/options

    Returns the parsed JSON response on success, or None on failure.
    """
    base_url = settings.STRAPI_API_BASE_URL

    if not base_url or not settings.STRAPI_API_TOKEN:
        logger.error(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )
        return None

    url = f"{base_url.rstrip('/')}/partner-configurations/options"
    session = get_cms_session()
    headers = get_cms_headers()

    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        logger.error(
            "HTTP error fetching partner configuration options from CMS: %s", exc
        )
    except requests.exceptions.RequestException as exc:
        logger.error(
            "Error fetching partner configuration options from CMS: %s", exc
        )
    return None


def sync_locales_from_partner_configuration_options(locales=[]):
    """
    Upsert locales into content.Locale.

    If `locales` is not provided, options are fetched from
    /partner-configurations/options and `payload["locales"]` is used.

    Returns:
        dict: {"created": int, "updated": int, "skipped": int}
        None: if options payload fetch fails when locales are not passed
    """
    try:
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in locales:
            code = (item.get("code") or "").strip()
            name = (item.get("name") or "").strip()
            if not code or not name:
                skipped_count += 1
                continue

            _, created = Locale.all_objects.update_or_create(
                code=code,
                defaults={"name": name, "is_deleted": False},
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return {
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
        }
    except Exception:
        logger.exception("sync_locales_from_partner_configuration_options: Unexpected error while syncing locales from partner configuration options")
        return {
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "error": "An unexpected error occurred during locale sync. Check logs for details."
        }

def _parse_work_sector(item):
    if isinstance(item, str):
        raw_value = item.strip()
    else:
        return "", ""

    if not raw_value:
        return "", ""

    match = re.match(r"^(?P<slug>.+?)\s*\((?P<display_name>.+)\)$", raw_value)
    if match:
        return match.group("slug").strip(), match.group("display_name").strip()

    return raw_value, raw_value


def sync_work_sectors_from_partner_configuration_options(work_sectors=[]):
    """
    Upsert work sectors into content.WorkSector.

    Accepts either a list of strings or a list of objects.
    Values like `agriculture (Agriculture)` are parsed into
    slug=`agriculture` and display_name=`Agriculture`.
    """
    try:
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in work_sectors:
            slug, display_name = _parse_work_sector(item)
            if not slug or not display_name:
                skipped_count += 1
                continue

            _, created = WorkSector.all_objects.update_or_create(
                slug=slug,
                defaults={"display_name": display_name, "is_deleted": False},
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return {
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
        }
    except Exception:
        logger.exception("sync_work_sectors_from_partner_configuration_options: Unexpected error while syncing work sectors from partner configuration options")
        return {
            
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "error": "An unexpected error occurred during work sector sync. Check logs for details."
        }
        

def sync_collections_from_partner_configuration_options(collections=[]):
    """
    Upsert collections into content.Collection.

    Accepts either a list of objects.
    For object payloads, `apiName` is treated as the
    stable identifier and `name` as the display value.
    """
    try:
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in collections:
            name =  (item.get("displayName") or "").strip()
            api_name = (item.get("apiName") or "").strip()
            if not name or not api_name:
                logger.warning(
                    "Skipping collection with missing api_name or name: %s",
                    item,
                )
                skipped_count += 1
                continue

            _, created = Collection.all_objects.update_or_create(
                api_name=api_name,
                defaults={"name": name, "is_deleted": False},
            )
            print(f"Processed collection: api_name={api_name}, name={name}, created={created}")

            if created:
                created_count += 1
            else:
                updated_count += 1

        return {
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
        }
    except Exception:
        logger.exception("sync_collections_from_partner_configuration_options: Unexpected error while syncing collections from partner configuration options")
        return {
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "error": "An unexpected error occurred during collection sync. Check logs for details."
        }


def sync_partner_config_options():
    """
    Sync partner configuration options from CMS.

    Currently syncs locales, work sectors, and collections into content and returns
    fetch counts + sync summaries.
    """
    try:
        payload = get_partner_configuration_options()
        if payload is None:
            logger.error("Failed to fetch partner configuration options from CMS.")
            return None

        locales = payload.get("locales", [])
        work_sectors = payload.get("work_sectors", []) 
        collections = payload.get("collections", [])

        locale_summary = sync_locales_from_partner_configuration_options(locales=locales)

        work_sector_summary = sync_work_sectors_from_partner_configuration_options(
            work_sectors=work_sectors
        )

        collection_summary = sync_collections_from_partner_configuration_options(
            collections=collections
        )

        return {
            "locale_sync": locale_summary,
            "work_sector_sync": work_sector_summary,
            "collection_sync": collection_summary,
        }
    except Exception:
        logger.exception("sync_partner_config_options: Unexpected error while syncing partner configuration options")
        return None


