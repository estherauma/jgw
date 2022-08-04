from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
QueryMap = Dict[str, list[str]]


class CheckLists(BaseAnalytics):
    def __init__(self, key) -> None:
        checklists_data, clean = api.get_data(key=key)
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(checklists_data)
        self.export_csv_name = f"{key}-checklists.csv"

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None, df=None):
        return_fields = fields or ["route", "locale"]
        _df = self.get_df(filters)
        _stats = {field: self.get_count(field, _df) for field in return_fields}
        return _stats
