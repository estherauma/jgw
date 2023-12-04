import json
import os
from abc import abstractmethod, ABC

import requests

from common.const.value_const import APPLICATION_POSSIBLE_START_DATE
from common.services.api_client import JustGoodWorkAPIClient
from common.utils.date_utils import todays_date


class JsonFileDataCache(ABC):
    def __init__(self, file_name):
        self.file_name = file_name

    def get_data(self, update_data=False):
        if not update_data and os.path.exists(self.file_name):
            with open(self.file_name, "r", encoding="utf-8") as file:
                cached_data = json.load(file)
                return cached_data.get("data")

        # if not fetch data from the api
        data = self.fetch_data_from_api()
        if data:
            self.cache_data(data)
            return data.get("data")

    @abstractmethod
    def fetch_data_from_api(self):
        pass

    def cache_data(self, data):
        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)


class InlineQuestionDataCache(JsonFileDataCache):
    def __init__(self):
        super().__init__("dev/data/inline_questions.json")

    def fetch_data_from_api(self, jgw_api_client=JustGoodWorkAPIClient()):
        start_date = APPLICATION_POSSIBLE_START_DATE
        end_date = todays_date()
        data = jgw_api_client.get_data(f"/inlinequestions?startDate={start_date}&endDate={end_date}")
        return {"data": data}


def run():
    # add inline questions
    InlineQuestionDataCache().get_data()
