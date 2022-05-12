from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
QueryMap = Dict[str, list[str]]


class Inline(BaseAnalytics):
    def __init__(self) -> None:
        inline_data = api.get_data(key='inline')
        self.df = pd.DataFrame.from_records(inline_data)
        self.export_csv_name = "inline_qn_responses.csv"

    def get_stats_object(
        self, fields: list[str] = None, filters: QueryMap = None, df=None
    ):
        return_fields = fields or ["route", "locale", "language"]
        _df = self.get_df(filters)
        _stats = {
            "data": {field: self.get_count(field, _df) for field in return_fields}
        }
        _stats["response_count"] = len(_df)
        return _stats
