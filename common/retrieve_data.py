"""
    JGW API helpers
"""
import os

import requests
from requests.exceptions import HTTPError


class JGWApi:
    def __init__(self) -> None:
        self.base_url = os.getenv("JGW_API")
        self.session = requests.Session()

    def _get(self, url, params) -> requests.Response:
        _response = None
        try:
            _response = self.session.get(url, params=params)
            _response.raise_for_status()
        except HTTPError as err:
            # sentry? logging? throw error to caller?
            print("Error fetching data", err)
        return _response

    def _get_data(self, url) -> list:
        url = f"{self.base_url}{url}"
        response = self._get(url, {})
        if response and response.status_code == requests.codes.ok:
            result = response.json()
            data = result["data"]
            return data
        return None

    def get_preferences(self):
        return self._get_data(url="/api/v2/preferences")

    def get_inline_question_responses(self):
        return self._get_data("/api/v2/inlinequestions")

    def get_messaging_question_responses(self):
        return self._get_data("/api/v2/messaging-questions")
