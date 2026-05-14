from datetime import datetime,timezone
import json
import logging
import re
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from common.const.value_const import CMS_SYNC_FAILED, CMS_SYNC_SUCCESS
from content.models import Collection, Locale, WorkSector
from preference.models import (
    OrganizationGroup,
    OrganisationAccessCode,
    OrganisationData,
    SiteLanguages,
)
from content.services.utils import get_cms_headers, get_cms_session
from user_management.roles import add_default_org_roles
from user_management.models import WorkGroup

logger = logging.getLogger(__name__)


class FileUploadError(Exception):
    pass


class PartnerConfigurationSyncError(Exception):
    pass


def _build_media_url(url):
    if not url:
        return ""

    base_url = (settings.STRAPI_API_BASE_URL or "").removesuffix("/api")
    return urljoin(f"{base_url}/", url.lstrip("/"))

def upload_files_to_cms(files):
    """Upload organization asset files to CMS.

    Args:
        files (list): File-like objects ready to be posted to the CMS upload API.

    Returns:
        list[dict]: Uploaded file metadata with `id`, `name`, and resolved `url`.

    Raises:
        FileUploadError: If CMS configuration is missing, no files are provided,
            or the upload fails.
    """
    base_url = settings.STRAPI_API_BASE_URL
    token = settings.STRAPI_API_TOKEN
    if not base_url or not token:
        raise FileUploadError(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )

    if not files:
        raise FileUploadError("No files provided for upload.")

    url = f"{base_url.rstrip('/')}/upload"
    session = get_cms_session()
    headers = {
          "Authorization": f"Bearer {settings.STRAPI_API_TOKEN}",
    }
    form_files = [("files", file_obj) for file_obj in files]

    try:
        response = session.post(
            url,
            headers=headers,
            files=form_files,
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
    except  Exception as exc:
        logger.error("HTTP error uploading file to Strapi: %s", exc)
        raise FileUploadError("Failed to upload files to Strapi.") from exc

    if not isinstance(payload, list) or not payload:
        raise FileUploadError("Strapi upload did not return a file URL.")

    uploaded_urls = []
    for item in payload:
        url = _build_media_url(item.get("url"))
        if not url:
            logger.warning("Strapi upload response item missing URL: %s", item)
            continue
        
        uploaded_urls.append({
            "id": item.get("id"), 
            "name": item.get("name"),
            "url": url
            })
    if not uploaded_urls:
        raise FileUploadError("Strapi upload did not return a valid file URL.")

    return uploaded_urls


def _format_collection_languages_for_cms(site_languages):
    return [
        {
            "type": "paragraph",
            "children": [
                {
                    "type": "text",
                    "text": site_language.code,
                }
            ],
        }
        for site_language in site_languages
        if site_language.code
    ]


def _format_work_sector_for_cms(work_sector_slug):
    if not work_sector_slug:
        return None

    work_sector = WorkSector.objects.filter(slug=work_sector_slug).first()
    if not work_sector:
        return work_sector_slug

    return f"{work_sector.slug} ({work_sector.display_name})"

def _build_access_code_value_for_cms(organisation):
    organisation_access_codes = OrganisationAccessCode.objects.filter(
        organisation=organisation,
    ).order_by("created_at")
    return ",".join(
        access_code.code for access_code in organisation_access_codes if access_code.code
    )


def _build_user_groups_payload_for_cms(organisation):
    work_groups = WorkGroup.objects.filter(organisation=organisation).prefetch_related(
        "access_codes"
    )
    payload = []
    for work_group in work_groups:
        access_codes = [
            access_code.code
            for access_code in work_group.access_codes.order_by("created_at")
            if access_code.code
        ]
        payload.append(
            { 
                #CMS expects access codes  in this format: "YEL2\nYEL3" , "YEL2"
                "access_codes": "\n".join(access_codes),
                "name": work_group.name,
                "data_platform_ref": str(work_group.id),
            }
        )

    return payload


def _get_organisation_site_languages(organisation):
    return list(
        SiteLanguages.objects.filter(organisation=organisation).order_by("code")
    )


def _build_org_payload_for_cms(organisation):
    site_languages = _get_organisation_site_languages(organisation)
    payload = {
        "name": organisation.name,
        "display_name": organisation.display_name or organisation.name,
        "content_collection": organisation.content_collection,
        "has_custom_content": organisation.has_custom_content,
        "access_code": _build_access_code_value_for_cms(organisation),
        "work_sector": _format_work_sector_for_cms(organisation.work_sector),
        "big_icon": organisation.big_icon_cms_media_id,
        "small_icon": organisation.small_icon_cms_media_id,
        "theme": organisation.theme or None,
        "default_collection_language": organisation.default_collection_language or "",
        "collection_languages": _format_collection_languages_for_cms(site_languages),
        "default_report_issue_emails": organisation.default_report_issue_emails or "",
        "default_feedback_emails": organisation.default_feedback_emails or "",
        "user_groups": _build_user_groups_payload_for_cms(organisation),
    }
    if payload["work_sector"] is None:
        payload.pop("work_sector")
    if payload["theme"] is None:
        payload.pop("theme")
    return payload


def _build_existing_sites_lookup(existing_group_config={}):
    if not isinstance(existing_group_config, dict):
        return {}

    lookup = {}
    sites = existing_group_config.get("sites") or  existing_group_config.get('attributes', {}).get('sites') or []
    for site in sites:
        if not isinstance(site, dict):
            continue
        site_code = (site.get("site_code") or "").strip()
        if site_code:
            lookup[site_code] = site
    return lookup


def _build_group_partner_configuration_payload(
    organisation,
    existing_group_config=None,
    orgs_to_sync_ids=None,
    orgs_to_exclude_ids=None,
):
    organization_group = organisation.organization_group
    existing_sites_by_code = _build_existing_sites_lookup(existing_group_config)
    organizations = organization_group.organizations.order_by("name")
    if orgs_to_sync_ids:
        organizations = organizations.filter(
            models.Q(id__in=orgs_to_sync_ids)
            | models.Q(org_code__in=existing_sites_by_code.keys())
        ).distinct()
    if orgs_to_exclude_ids:
        organizations = organizations.exclude(id__in=orgs_to_exclude_ids)

    sites_payload = []
    for grouped_organisation in organizations:
        site_payload = _build_org_payload_for_cms(grouped_organisation)
        site_payload["site_code"] = grouped_organisation.org_code
        existing_site = existing_sites_by_code.get(grouped_organisation.org_code)
        if existing_site and existing_site.get("id") is not None:
            site_payload["id"] = existing_site.get("id")
        sites_payload.append(site_payload)

    return {
        "data": {
            "org_code": organization_group.group_code,
            "name": organization_group.name,
            "display_name": organization_group.name,
            "custom_type": organization_group.custom_type,
            "sites": sites_payload,
        }
    }


def build_partner_configuration_payload(
    organisation,
    existing_group_config=None,
    orgs_to_sync_ids=None,
    orgs_to_exclude_ids=None,
):
    payload_data = _build_org_payload_for_cms(organisation)
    if organisation.organization_group_id:
        return _build_group_partner_configuration_payload(
            organisation,
            existing_group_config=existing_group_config,
            orgs_to_sync_ids=orgs_to_sync_ids,
            orgs_to_exclude_ids=orgs_to_exclude_ids,
        )
    else:
        payload_data["org_code"] = organisation.org_code
        payload_data["custom_type"] = organisation.custom_type
        return {"data": payload_data}

 


def _extract_partner_configuration_cms_id(payload):
    if not isinstance(payload, dict):
        return None

    data = payload.get("data")
    if isinstance(data, dict):
        return data.get("id")

    return payload.get("id")


def _with_rebublish_flag(payload):
    if not isinstance(payload, dict):
        return payload
    updated_payload = dict(payload)
    updated_payload['data']["force_publish"] = True
    return updated_payload


def get_partner_configuration_by_id(cms_id):
    """Fetch one CMS partner configuration by its id endpoint."""
    base_url = settings.STRAPI_API_BASE_URL

    if not base_url or not settings.STRAPI_API_TOKEN:
        logger.error(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )
        return None

    if not cms_id:
        return None

    url = f"{base_url.rstrip('/')}/partner-configurations/{cms_id}"
    session = get_cms_session()
    headers = get_cms_headers()

    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data")
    except requests.exceptions.HTTPError as exc:
        logger.error("HTTP error fetching partner configuration by id from CMS: %s", exc)
    except requests.exceptions.RequestException as exc:
        logger.error("Error fetching partner configuration by id from CMS: %s", exc)
    return None


def _mark_organisation_sync_success(organisation, cms_id=None):
    organisation.cms_sync_status = CMS_SYNC_SUCCESS
    organisation.last_cms_sync_date = timezone.now()
    update_fields = ["cms_sync_status", "last_cms_sync_date"]
    if cms_id is not None:
        organisation.cms_id = str(cms_id)
        update_fields.append("cms_id")
    organisation.save(update_fields=update_fields)


def _mark_organisation_sync_failed(organisation):
    organisation.cms_sync_status = CMS_SYNC_FAILED
    organisation.last_cms_sync_date = timezone.now()
    organisation.save(update_fields=["cms_sync_status", "last_cms_sync_date"])


def _mark_group_sync_success(organization_group, cms_id=None):
    organization_group.cms_sync_status = CMS_SYNC_SUCCESS
    organization_group.last_cms_sync_date = timezone.now()
    update_fields = ["cms_sync_status", "last_cms_sync_date"]
    if cms_id is not None:
        organization_group.cms_id = str(cms_id)
        update_fields.append("cms_id")
    organization_group.save(update_fields=update_fields)


def _mark_group_sync_failed(organization_group):
    organization_group.cms_sync_status = CMS_SYNC_FAILED
    organization_group.last_cms_sync_date = timezone.now()
    organization_group.save(update_fields=["cms_sync_status", "last_cms_sync_date"])


def _get_existing_group_config(organization_group):
    group_config = None
    if organization_group.cms_id:
        group_config = get_partner_configuration_by_id(organization_group.cms_id)
    return group_config


def get_group_partner_configuration_sites_by_code(organization_group):
    if not organization_group.cms_id:
        return {}

    group_config = get_partner_configuration_by_id(organization_group.cms_id)
    if group_config is None:
        return None

    return _build_existing_sites_lookup(group_config)


def sync_group_partner_configuration_to_cms(
    organisation,
    orgs_to_sync_ids=None,
    orgs_to_exclude_ids=None,
):
    organization_group = organisation.organization_group
    if not organization_group:
        raise PartnerConfigurationSyncError(
            "Organisation is not assigned to an organization group."
        )

    base_url = settings.STRAPI_API_BASE_URL
    if not base_url or not settings.STRAPI_API_TOKEN:
        raise PartnerConfigurationSyncError(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )

    existing_group_config = _get_existing_group_config(organization_group)
    payload = build_partner_configuration_payload(
        organisation,
        existing_group_config=existing_group_config,
        orgs_to_sync_ids=orgs_to_sync_ids,
        orgs_to_exclude_ids=orgs_to_exclude_ids,
    )
    headers = get_cms_headers()

    try:
        if existing_group_config:
            cms_id = existing_group_config.get("id") 
            url = f"{base_url.rstrip('/')}/partner-configurations/{cms_id}"
            print(f"Updating existing group partner configuration in CMS with id={_with_rebublish_flag(payload).get('data', {}).get('sites')}")
            response = requests.put(
                url,
                headers=headers,
                json=_with_rebublish_flag(payload),
                timeout=30,
            )
        else:
            url = f"{base_url.rstrip('/')}/partner-configurations"
            response = requests.post(url, headers=headers, json=payload, timeout=30)

        response.raise_for_status()
        response_payload = response.json()
        cms_id = response_payload.get("data", {}).get("id")
        _mark_organisation_sync_success(organisation)
        _mark_group_sync_success(organization_group, cms_id=cms_id)
        return response_payload
    except Exception as exc:
        _mark_organisation_sync_failed(organisation)
        _mark_group_sync_failed(organization_group)
        logger.error(
            "HTTP error syncing organization group partner configuration to CMS: %s body=%s",
            exc,
            exc.response.text if getattr(exc, "response", None) is not None else "",
        )
        raise PartnerConfigurationSyncError(
            "Failed to sync organization group partner configuration to CMS."
        ) from exc


def delete_partner_configuration_from_cms(cms_id):
    base_url = settings.STRAPI_API_BASE_URL

    if not base_url or not settings.STRAPI_API_TOKEN:
        raise PartnerConfigurationSyncError(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )

    if not cms_id:
        return

    url = f"{base_url.rstrip('/')}/partner-configurations/{cms_id}"
    try:
        response = requests.delete(url, headers=get_cms_headers(), timeout=30)
        response.raise_for_status()
    except Exception as exc:
        logger.error(
            "HTTP error deleting partner configuration from CMS: %s body=%s",
            exc,
            exc.response.text if getattr(exc, "response", None) is not None else "",
        )
        raise PartnerConfigurationSyncError(
            "Failed to delete the existing organization partner configuration from CMS."
        ) from exc


def move_partner_configuration_to_group_in_cms(organisation):
    if not organisation.organization_group_id:
        raise PartnerConfigurationSyncError(
            "Organisation is not assigned to an organization group."
        )
    sync_response = sync_group_partner_configuration_to_cms(
        organisation,
        orgs_to_sync_ids=[organisation.id],
    )

    if organisation.cms_id:
        delete_partner_configuration_from_cms(organisation.cms_id)
        organisation.cms_id = None
        organisation.save(update_fields=["cms_id"])

    return sync_response


def remove_partner_configuration_from_group_in_cms(organisation):
    organization_group = organisation.organization_group
    if not organization_group:
        raise PartnerConfigurationSyncError(
            "Organisation is not assigned to an organization group."
        )

    if organization_group.cms_id:
        sync_group_partner_configuration_to_cms(
            organisation,
            orgs_to_exclude_ids=[organisation.id],
        )

    organisation.organization_group = None
    update_partner_configuration_in_cms(organisation)
    return organisation


def resolve_partner_configuration_cms_id(organisation):
    if organisation.organization_group_id:
        return None

    if organisation.cms_id:
        return organisation.cms_id

    partner_configuration = get_partner_configuration_by_org_code(organisation.org_code)
    cms_id = partner_configuration.get("id") if partner_configuration else None
    if not cms_id:
        return None

    organisation.cms_id = str(cms_id)
    organisation.save(update_fields=["cms_id"])
    return organisation.cms_id


def execute_partner_configuration_cms_update(*, organisation, url, payload, error_message):
    try:
        response = requests.put(
            url,
            headers=get_cms_headers(),
            json=_with_rebublish_flag(payload),
            timeout=30,
        )
        response.raise_for_status()
        _mark_organisation_sync_success(organisation)
        return response.json()
    except Exception as exc:
        _mark_organisation_sync_failed(organisation)
        logger.error(
            "HTTP error updating partner configuration in CMS: %s body=%s",
            exc,
            exc.response.text if exc.response is not None else "",
        )
        raise PartnerConfigurationSyncError(error_message) from exc

def update_partner_configuration_in_cms(organisation):
    """Update the CMS partner configuration for an organization.

    Args:
        organisation (OrganisationData): The organization whose partner
            configuration should be synced.

    Returns:
        dict: The CMS response payload.

    Raises:
        PartnerConfigurationSyncError: If CMS configuration is missing or the
            update fails.
    """
    if organisation.organization_group_id:
        return sync_group_partner_configuration_to_cms(organisation)

    base_url = settings.STRAPI_API_BASE_URL
    cms_id = resolve_partner_configuration_cms_id(organisation)

    if not base_url or not settings.STRAPI_API_TOKEN:
        raise PartnerConfigurationSyncError(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )

    if not cms_id:
        return add_partner_configuration_to_cms(organisation)

    url = f"{base_url.rstrip('/')}/partner-configurations/{cms_id}"
    payload = build_partner_configuration_payload(organisation)
    return execute_partner_configuration_cms_update(
        organisation=organisation,
        url=url,
        payload=payload,
        error_message="Failed to update partner configuration in CMS.",
    )

def update_partner_configuration_work_codes_in_cms(
    organisation,
    *,
    fields_to_update=None,
):
    """Update work-code related CMS fields for an organization.

    Args:
        organisation (OrganisationData): The organization whose partner
            configuration fields should be updated.
        fields_to_update (list[str] | None): Optional subset of fields to patch.
            Supported values are `access_code` and `user_groups`.

    Returns:
        dict: The CMS response payload.

    Raises:
        PartnerConfigurationSyncError: If CMS configuration is missing or the
            update fails.
    """
    if organisation.organization_group_id:
        return sync_group_partner_configuration_to_cms(organisation)

    base_url = settings.STRAPI_API_BASE_URL
    cms_id = resolve_partner_configuration_cms_id(organisation)

    if not base_url or not settings.STRAPI_API_TOKEN:
        raise PartnerConfigurationSyncError(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )

    if not cms_id:
        return update_partner_configuration_in_cms(organisation)

    url = f"{base_url.rstrip('/')}/partner-configurations/{cms_id}"
    selected_fields = fields_to_update or ["access_code"]
    payload_data = {}
    if "access_code" in selected_fields:
        payload_data["access_code"] = _build_access_code_value_for_cms(organisation)
    if "user_groups" in selected_fields:
        payload_data["user_groups"] = _build_user_groups_payload_for_cms(organisation )
    payload = {"data": payload_data}
    return execute_partner_configuration_cms_update(
        organisation=organisation,
        url=url,
        payload=payload,
        error_message="Failed to update partner configuration work codes in CMS.",
    )

def add_partner_configuration_to_cms(organisation):
    """Create a CMS partner configuration for an organization.

    Args:
        organisation (OrganisationData): The organization to create in CMS.

    Returns:
        dict: The CMS response payload.

    Raises:
        PartnerConfigurationSyncError: If CMS configuration is missing or the
            create request fails.
    """
    if organisation.organization_group_id:
        return sync_group_partner_configuration_to_cms(organisation)

    base_url = settings.STRAPI_API_BASE_URL

    if not base_url or not settings.STRAPI_API_TOKEN:
        raise PartnerConfigurationSyncError(
            "STRAPI_API_BASE_URL or STRAPI_API_TOKEN is not configured."
        )

    url = f"{base_url.rstrip('/')}/partner-configurations"
    headers = get_cms_headers()
    payload = build_partner_configuration_payload(organisation)

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        response_payload = response.json()
        cms_id = _extract_partner_configuration_cms_id(response_payload)
        _mark_organisation_sync_success(organisation, cms_id=cms_id)
        return response_payload
    except Exception as exc:
        _mark_organisation_sync_failed(organisation)
        logger.error(
            "HTTP error posting partner configuration to CMS: %s body=%s",
            exc,
            exc.response.text if exc.response is not None else "",
        )
        raise PartnerConfigurationSyncError(
            "Failed to add partner configuration to CMS."
        ) from exc

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


def sync_organisation_user_groups(organisation, user_groups):
    if not isinstance(user_groups, list):
        return 0

    synced_count = 0
    for item in user_groups:
        group_name = (item.get("name") or "").strip()
        if not group_name:
            continue

        work_group, _ = WorkGroup.all_objects.update_or_create(
            organisation=organisation,
            name=group_name,
            defaults={"is_deleted": False, "deleted_at": None, "deleted_by": None},
        )

        access_codes = item.get("access_codes")
        if isinstance(access_codes, str):
            access_codes = [
                code.strip() for code in access_codes.splitlines() if code and code.strip()
            ]
        elif isinstance(access_codes, list):
            access_codes = [
                str(code).strip() for code in access_codes if str(code).strip()
            ]
        else:
            access_codes = []

        synced_access_codes = []
        for access_code_value in access_codes:
            access_code, _ = OrganisationAccessCode.objects.update_or_create(
                code=access_code_value,
                defaults={"organisation": organisation},
            )
            synced_access_codes.append(access_code)

        work_group.access_codes.set(synced_access_codes)

        synced_count += 1

    return synced_count


def sync_organisation_partner_configuration_item(*, org_code, defaults, item):
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
    user_groups_synced = sync_organisation_user_groups(
        organisation=organisation,
        user_groups=item.get("user_groups")
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
        "organisation": organisation,
        "created": created,
        "languages_created": languages_created,
        "user_groups_synced": user_groups_synced,
    }


def build_organisation_partner_configuration_defaults(
    *, item, organization_group=None, cms_id=None
):
    big_icon = item.get("big_icon")
    small_icon = item.get("small_icon")

    defaults = {
        "name": item.get("name"),
        "display_name": item.get("display_name"),
        "has_custom_content": item.get("has_custom_content", False),
        "custom_type": item.get("custom_type") or "version_1",
        "work_sector": item.get("work_sector"),
        "content_collection": item.get("content_collection"),
        "default_collection_language": item.get("default_collection_language"),
        "default_report_issue_emails": item.get("default_report_issue_emails"),
        "default_feedback_emails": item.get("default_feedback_emails"),
        "theme": item.get("theme"),
        "big_icon": _build_media_url(big_icon.get("url")) if big_icon else "",
        "big_icon_cms_media_id": big_icon.get("id") if big_icon else None,
        "small_icon": _build_media_url(small_icon.get("url")) if small_icon else "",
        "small_icon_cms_media_id": small_icon.get("id") if small_icon else None,
    }

    if organization_group is not None:
        defaults["organization_group"] = organization_group

    if cms_id is not None:
        defaults["cms_id"] = cms_id

    return defaults


def sync_organization_group_partner_configuration_item(item):
    group_code = (item.get("org_code") or "").strip()
    if not group_code:
        logger.warning(
            "Skipping organization group partner configuration with missing group code: %s",
            item,
        )
        return {
            "created": 0,
            "updated": 0,
            "languages_created": 0,
            "user_groups_synced": 0,
        }

    group_defaults = {
        "name": item.get("name"),
        "custom_type": item.get("custom_type"),
        "cms_id": str(item.get("id")) 
    }

    with transaction.atomic():
        organization_group, group_created = OrganizationGroup.objects.update_or_create(
            group_code=group_code,
            defaults=group_defaults,
        )

        results = {
            "created": 1 if group_created else 0,
            "updated": 0 if group_created else 1,
            "languages_created": 0,
            "user_groups_synced": 0,
        }

        for site in item.get("sites") or []:
            site_code = (site.get("site_code") or "").strip()
            if not site_code:
                logger.warning(
                    "Skipping organization group site with missing site_code: %s",
                    site,
                )
                continue

            defaults = build_organisation_partner_configuration_defaults(
                item=site,
                organization_group=organization_group,
            )

            sync_result = sync_organisation_partner_configuration_item(
                org_code=site_code,
                defaults=defaults,
                item=site,
            )
            results["languages_created"] += sync_result["languages_created"]
            results["user_groups_synced"] += sync_result["user_groups_synced"]

            if sync_result["created"]:
                results["created"] += 1
            else:
                results["updated"] += 1

        return results

def sync_partner_configuration_item(item):
    """Sync a single CMS partner-configuration record into local data.

    Args:
        item (dict): One CMS partner-configuration record.

    Returns:
        dict: Sync counters including `created`, `updated`,
        `languages_created`, and `user_groups_synced`.
    """
    org_code = (item.get("org_code") or "").strip()
    custom_type = (item.get("custom_type"
    ) or "").strip()

    if not org_code:
        logger.warning(
            "Skipping partner configuration with missing org_code: %s",
            item,
        )
        return {"created": 0, "updated": 0, "languages_created": 0, "user_groups_synced": 0}

    if custom_type == "organization_group":
        return sync_organization_group_partner_configuration_item(item)

    defaults = build_organisation_partner_configuration_defaults(
        item=item,
        cms_id=item.get("id"),
    )

    with transaction.atomic():
        sync_result = sync_organisation_partner_configuration_item(
            org_code=org_code,
            defaults=defaults,
            item=item,
        )

    return {
        "created": 1 if sync_result["created"] else 0,
        "updated": 0 if sync_result["created"] else 1,
        "languages_created": sync_result["languages_created"],
        "user_groups_synced": sync_result["user_groups_synced"],
    }

def sync_partner_configurations():
    """Sync all CMS partner-configuration records into local data.

    Returns:
        dict | None: Aggregate sync counters on success, otherwise `None`.
    """
    try:
        items = get_partner_configurations()
        if items is None:
            return None


        created_count = 0
        updated_count = 0
        languages_created_count = 0
        user_groups_synced_count = 0

        for item in items:
            result = sync_partner_configuration_item(item)
            created_count += result["created"]
            updated_count += result["updated"]
            languages_created_count += result["languages_created"]
            user_groups_synced_count += result["user_groups_synced"]

        return {
            "created": created_count,
            "updated": updated_count,
            "languages_created": languages_created_count,
            "user_groups_synced": user_groups_synced_count,
        }
    except Exception:
        logger.exception("Unexpected error while syncing partner configurations")
        return None

def get_partner_configurations(query_params=None):
    """Fetch partner-configuration records from the CMS.

    Args:
        query_params (dict | None): Optional query parameters passed to the CMS
            request.

    Returns:
        list[dict] | None: The CMS `data` list on success, otherwise `None`.
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
    params = query_params or {}

    try:
        response = session.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.HTTPError as exc:
        logger.error("HTTP error fetching partner configurations from CMS: %s", exc)
    except requests.exceptions.RequestException as exc:
        logger.error("Error fetching partner configurations from CMS: %s", exc)
    return None

def get_partner_configuration_by_org_code(org_code, publication_state="draft"):
    """Fetch one CMS partner configuration by its top-level org code.

    Args:
        org_code (str): Top-level `org_code` value in CMS.
        publication_state (str): CMS publication state filter.

    Returns:
        dict | None: The first matching CMS record, otherwise `None`.
    """
    response = get_partner_configurations(
        query_params={
            "filters[org_code][$eq]": org_code,
            "publicationState": publication_state,
        },
    )
    return response[0] if response else None

def get_partner_configuration_options():
    """Fetch partner-configuration option values from the CMS.

    Returns:
        dict | None: The parsed CMS options payload, otherwise `None`.
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
    """Sync CMS locale options into the local Locale table.

    Args:
        locales (list[dict]): Locale option records from CMS.

    Returns:
        dict: Counters for `created`, `updated`, and `skipped`, plus `error`
        when an unexpected failure occurs.
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
    """Sync CMS work-sector options into the local WorkSector table.

    Args:
        work_sectors (list): Work-sector option values from CMS.

    Returns:
        dict: Counters for `created`, `updated`, and `skipped`, plus `error`
        when an unexpected failure occurs.
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
    """Sync CMS collection options into the local Collection table.

    Args:
        collections (list[dict]): Collection option records from CMS.

    Returns:
        dict: Counters for `created`, `updated`, and `skipped`, plus `error`
        when an unexpected failure occurs.
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
    """Sync all CMS partner-configuration option sets into local lookup tables.

    Returns:
        dict | None: Per-option-set sync summaries on success, otherwise `None`.
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
