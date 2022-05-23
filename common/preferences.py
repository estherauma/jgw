from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
QueryMap = Dict[str, list[str]]


class Preferences(BaseAnalytics):
    def __init__(self) -> None:
        preferences = api.get_data(key='preferences')
        self.raw_df = pd.DataFrame.from_records(preferences)
        self.export_csv_name = "preferences.csv"

    def get_stats_object(self, fields: list[str] = None, filters: QueryMap = None):
        return_fields = fields or ["age", "gender"]
        _df = self.get_df(filters)
        _stats = {field: self.get_count(field, _df) for field in return_fields}
        return _stats
