"""JGW API helpers
"""
import json
import os
from typing import Dict

import pandas as pd
import requests
from jgwpandas.settings import PROJECT_ROOT

FILENAMES = {
    k: os.path.join(PROJECT_ROOT, f"static/assets/data/{k}.xlsx")
    for k in ["preferences", "inline", "messaging", "help_contacts"]
}
URLS = {
    "preferences": "/preferences",
    "inline": "/inlinequestions",
    "messaging": "/messaging-questions",
    "help_contacts": "/help-contacts",
}


class JGWApi:
    def __init__(self) -> None:
        self.base_url = os.getenv("JGW_API")
        self.session = requests.Session()

    def _get(self, url, params) -> requests.Response:
        _response = None
        _response = self.session.get(url, params=params)
        _response.raise_for_status()
        return _response

    def get_data(self, key: str) -> list:
        """`key` is one of: `preferences, inline, messaging, help_contacts`"""
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
                self.write_data_to_file(stats=data, key=key)
        return data

    def write_data_to_file(self, stats: list, key):
        filename = FILENAMES.get(key)
        df = pd.DataFrame.from_records(stats)
        df.to_excel(filename, index=False)

    def get_stats_from_file(self, key) -> Dict:
        filename = FILENAMES.get(key)
        df = pd.read_excel(filename)
        stats = df.to_dict(orient="records")
        return stats
