from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
QueryMap = Dict[str, list[str]]


class Messaging(BaseAnalytics):
    def __init__(self) -> None:
        messaging_data, clean = api.get_data(key="messaging")
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(messaging_data)
        self.export_csv_name = "messaging_qn_responses.csv"

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None, df=None):
        return_fields = fields or ["route", "locale"]
        _df = self.get_df(filters)
        if _df.empty:
            return {}
        _stats = {field: self.count_unique(field, _df) for field in return_fields}
        return _stats
