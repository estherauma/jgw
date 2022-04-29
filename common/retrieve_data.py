"""
    JGW API helpers
"""
import json
import os
from typing import Dict

import requests
from requests.exceptions import HTTPError

FILENAMES = {
    "preferences": "preferences.json",
    "inline": "inlinequestions.json",
    "messaging": "messaging-questions.json",
}
URLS = {
    "preferences": "/api/v2/preferences",
    "inline": "/api/v2/inlinequestions",
    "messaging": "/api/v2/messaging-questions",
}


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

    def get_data(self, key: str) -> list:
        """`key` is one of: `preferences, inline, messaging`"""
        if key not in FILENAMES.keys():
            return None
        data = None
        try:
            data = self.get_stats_from_file(key=key)
        except FileNotFoundError:
            url = f"{self.base_url}{URLS.get(key)}"
            response = self._get(url, {})
            if response and response.status_code == requests.codes.ok:
                result = response.json()
                data = result["data"]
                self.write_stats_to_file(stats=data, key=key)
        return data

    def write_stats_to_file(self, stats: list, key):
        filename = FILENAMES.get(key)
        with open(filename, "w") as f:
            json.dump(stats, f)
        

    def get_stats_from_file(self, key) -> Dict:
        filename = FILENAMES.get(key)
        stats = None
        with open(filename, "r") as f:
            stats = json.load(f)
        return stats
