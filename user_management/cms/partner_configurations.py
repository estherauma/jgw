import json
import logging

import requests
from django.conf import settings

from user_management.cms.utils import get_cms_headers, get_cms_session

logger = logging.getLogger(__name__)


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
