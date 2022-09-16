import os
from datetime import datetime
from functools import reduce
from typing import Dict

import pandas as pd
from jgwpandas.settings import CACHE_DIR

QueryMap = Dict[str, str]

unwanted_cols = ["", "deviceId", "undefined", "__v", "_id"]
demographic_cols = [
    "appId",
    "locale",
    "route",
    "language",
    "origin",
    "destination",
    "organisation",
    "factoryFarm",
    "createdAt",
    "updatedAt",
]
exclude_cols = [*unwanted_cols, *demographic_cols]


class BaseAnalytics:
    def __init__(self) -> None:
        self.export_csv_name = "export.csv"

    def get_df_path(self, query: Dict, extension="csv"):
        searchParam_list = [f"{k}_{v}" for k, v in query.items()]
        data_category = f"{type(self).__name__}"
        searchParam_list = f"_{'-'.join(searchParam_list)}" if searchParam_list else ""
        return os.path.join(CACHE_DIR, f"{data_category.lower()}{searchParam_list}.{extension}")

    def count_unique(self, field: str, df=None) -> Dict:
        _df = df if df is not None else self.raw_df
        return _df[field].value_counts().to_dict()

    def get_df(self, filters: QueryMap = None):
        _df = None
        if self.raw_df is not None:
            _df = self.raw_df.copy()
            if filters is not None:
                cachedResults_path = self.get_df_path(filters)
                try:
                    _df = pd.read_csv(cachedResults_path)
                except FileNotFoundError:
                    _df = reduce(self.filter_data, filters.items(), _df)
                    if self.cleaned:
                        _df.to_csv(cachedResults_path)
        return _df

    def filter_by_destination(self, destination: str, df):
        if "destination" in df.columns:
            destinations = df["destination"].astype("str")
            mask = destinations == destination
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

    def filter_by_timeRange(self, start_date: str, df):
        if start_date == "all_time":
            return df
        today = datetime.today().strftime("%Y-%m-%d")
        mask = df["createdAt"].between(start_date, today, inclusive="both")
        df = df.loc[mask]
        return df

    def filter_by_question(self, question: str, df):
        if question in df.columns:
            demographic_cols.append(question)
            mask = df[question].notnull()
            df = df.loc[mask]
            return df[demographic_cols]
        return pd.DataFrame()

    def filter_data(self, df, query):
        filter_map = {
            "destination": self.filter_by_destination,
            "origin": self.filter_by_origin,
            "scheme_name": self.filter_by_schemeName,
            "factory_farm": self.filter_by_factoryFarm,
            "time_range": self.filter_by_timeRange,
            "question": self.filter_by_question,
        }
        field, value = query
        filter_func = filter_map.get(field)
        if filter_func is not None:
            df = filter_func(value, df)
        return df
