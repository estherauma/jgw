import os
from typing import Dict

import pandas as pd
from jgwpandas.settings import CACHE_DIR
from pytz import country_names

QueryMap = Dict[str, str]


class BaseAnalytics:
    def __init__(self) -> None:
        self.export_csv_name = "export.csv"

    def export_csv(self):
        self.df.to_csv(self.export_csv_name)

    def get_df_path(self, query: Dict):
        kvString_list = [f"{k}_{v}" for k, v in query.items()]
        return os.path.join(CACHE_DIR, f"{type(self).__name__}_{'-'.join(kvString_list)}.pkl")

    def get_count(self, field: str, df=None):
        _df = df.copy() if df is not None else self.df.copy()
        return _df[field].value_counts().to_dict()

    def get_df(self, filters: QueryMap = None):
        _df = None

        if self.df is not None:
            _df = self.df.copy()

        if filters is not None:
            all_filters_path = self.get_df_path(filters)
            try:
                _df = pd.read_pickle(all_filters_path)
            except FileNotFoundError:
                for k in filters:
                    query = {k: filters[k]}
                    filter_path = self.get_df_path(query)
                    try:
                        _df = pd.read_pickle(filter_path)
                    except FileNotFoundError:
                        _df = self.filter_data(_df, query)
                _df.to_pickle(all_filters_path)
        return _df

    def filter_by_destination(self, destination: str, df):
        destination = destination.split(",")
        destination = [country_names.get(i).lower() for i in destination if bool(i)]
        _routes = df["route"].astype("str").str.lower()
        mask = _routes.str.endswith(tuple(destination))
        return df.loc[mask]

    def filter_by_origin(self, origin: str, df):
        origin = origin.split(",")
        origin = [country_names.get(i).lower() for i in origin if bool(i)]
        _routes = df["route"].astype("str").str.lower()
        mask = _routes.str.startswith(tuple(origin))
        return df.loc[mask]

    def filter_data(self, df, query: Dict):
        filter_map = {"destination": self.filter_by_destination, "origin": self.filter_by_origin}
        for field, value in query.items():
            filter_func = filter_map.get(field)
            if filter_func is not None:
                df = filter_func(value, df)
                df.to_pickle(self.get_df_path(query))
        return df
