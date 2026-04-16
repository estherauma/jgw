import json
import logging

import requests
from django.conf import settings
from django.db import transaction

from preference.models import OrganisationData, SiteLanguages
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
    print(f"Syncing partner configuration for org_code: {org_code}, name: {name}")

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
        print(
            "Successfully fetched partner configurations from CMS: %s",
            json.dumps(data, default=str),
        )
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
