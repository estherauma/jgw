import logging

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def get_cms_session(total_retries=3, backoff_factor=2, status_forcelist=None):
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


def get_cms_headers(content_type="application/json"):
    token = settings.STRAPI_API_TOKEN
    headers = {
          "Authorization": f"Bearer {token}",
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers
