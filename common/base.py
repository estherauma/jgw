import os
from datetime import datetime
from functools import reduce
from typing import Dict

import pandas as pd
from common.utils.helpers import save_as_excel 

from jgwpandas.settings import CACHE_DIR

from .retrieve_data import demographic_cols

QueryMap = Dict[str, str]


class BaseAnalytics:
    def __init__(self) -> None:
        self.export_csv_name = "export.csv"

    def count_unique(self, field: str, df=None) -> Dict:
        _df = df if df is not None else self.raw_df
        return _df[field].value_counts().to_dict()

    def get_df(self, filters: QueryMap = None):
        _df = pd.DataFrame()
        if not self.raw_df.empty:
            _df = self.raw_df.copy()
            if filters is not None:
                _df = reduce(self.filter_data, filters.items(), _df)
        return _df

    def filter_by_destination(self, destination: str, df):
        if "destination" in df.columns:
            destinations = df["destination"].astype("str")
            mask = destinations.isin(destination)
            return df[mask]
        return pd.DataFrame()

    def filter_by_origin(self, origin: str, df):
        if "origin" in df.columns:
            origins = df["origin"].astype("str")
            mask = origins == origin
            return df[mask]
        return pd.DataFrame()

    def filter_by_schemeName(self, scheme_name: str, df):
        if "organisation" in df.columns:
            _scheme_names = df["organisation"].astype("str").str.lower()
            mask = _scheme_names == scheme_name.lower()
            return df.loc[mask]
        return pd.DataFrame()

    def filter_by_factoryFarm(self, factory_farm: str, df):
        if "factoryFarm" in df.columns:
            _factory_farms = df["factoryFarm"].astype("str").str.lower()
            mask = _factory_farms == factory_farm.lower()
            return df.loc[mask]
        return pd.DataFrame()

    def filter_by_timeRange(self, time_range: str, df):
        start_date, end_date = time_range.split(",")
        save_as_excel(df, "hc_filter_by_timeRange")
        if start_date == "all_time":
            return df
        if "createdAt" in df.columns:
            mask = df["createdAt"].between(start_date, end_date, inclusive="both")
            df = df.loc[mask]
            return df
        return pd.DataFrame()

    def filter_by_question(self, question: str, df):
        if question in df.columns:
            demographic_cols.append(question)
            mask = df[question].notnull()
            df = df.loc[mask]
            return df[demographic_cols]
        return pd.DataFrame()

    def filter_by_organisation(self, org_name: str, df):
        if "organisation" in df.columns:
            return df.loc[df["organisation"] == org_name]
        return pd.DataFrame()

    def filter_data(self, df, query):
        filter_map = {
            "destination": self.filter_by_destination,
            "origin": self.filter_by_origin,
            "scheme_name": self.filter_by_schemeName,
            "factory_farm": self.filter_by_factoryFarm,
            "time_range": self.filter_by_timeRange,
            "question": self.filter_by_question,
            "organisation": self.filter_by_organisation,
        }
        field, value = query
        filter_func = filter_map.get(field)
        if filter_func is not None:
            df = filter_func(value, df)
        return df
