
from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
QueryMap = Dict[str, list[str]]

def clean_df(df):
    if "organisation" in df.columns:
        df["organisation"] = df["organisation"].str.replace("Seasonal Worker Scheme - ", "").str.replace("Seasonal  Worker Scheme -", "")
    return df

class Preferences(BaseAnalytics):
    def __init__(self) -> None:
        preferences, clean = api.get_data(key="preferences")
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(preferences)
        self.export_csv_name = "preferences.csv"

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None):
        return_fields = fields or ["age", "gender", "organisation"]
        _df = clean_df(self.get_df(filters))
        if _df.empty:
            return {}
        _stats = {field: self.count_unique(field, _df) for field in return_fields if field in _df.columns}
        return _stats
