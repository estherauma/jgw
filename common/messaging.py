from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
FilterList = Dict[str, list[str]]


class Messaging(BaseAnalytics):
    def __init__(self) -> None:
        messaging_data = api.get_messaging_question_responses()
        self.df = pd.DataFrame.from_records(messaging_data)
        self.export_csv_name = "messaging_qn_responses.csv"

    def get_stats_object(self, fields: list[str] = None, filters: FilterList = None, df=None):
        return_fields = fields or ["route", "locale"]
        _df = df.copy() if df is not None else self.filter_data(filters)
        _stats = {field: self.get_count(field, _df) for field in return_fields}
        return _stats
