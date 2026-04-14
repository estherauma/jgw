import logging

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def get_cms_session(total_retries=3, backoff_factor=2, status_forcelist=None):
    """
    Build and return a requests Session configured with retry/backoff logic.

    Args:
        total_retries: Number of times to retry on failure.
        backoff_factor: Multiplier for exponential backoff between retries.
        status_forcelist: HTTP status codes that should trigger a retry.

    Returns:
        A configured requests.Session instance.
    """
    if status_forcelist is None:
        status_forcelist = [500, 502, 503, 504]

    retry_strategy = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_cms_headers():
    token = settings.STRAPI_API_TOKEN
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
