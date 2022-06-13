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
        self.raw_df.to_csv(self.export_csv_name)

    def get_df_path(self, query: Dict, extension="pkl"):
        kvString_list = [f"{k}_{v}" for k, v in query.items()]
        return os.path.join(CACHE_DIR, f"{type(self).__name__}_{'-'.join(kvString_list)}.{extension}")

    def get_count(self, field: str, df=None):
        _df = df.copy() if df is not None else self.raw_df.copy()
        return _df[field].value_counts().to_dict()

    def get_df(self, filters: QueryMap = None):
        _df = None

        if self.raw_df is not None:
            _df = self.raw_df.copy()

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


    def filter_data(self, df, query: Dict):
        filter_map = {
            "destination": self.filter_by_destination,
            "origin": self.filter_by_origin,
            "scheme_name": self.filter_by_schemeName,
            "factory_farm": self.filter_by_factoryFarm,
        }
        for field, value in query.items():
            filter_func = filter_map.get(field)
            if filter_func is not None:
                df = filter_func(value, df)
                df.to_pickle(self.get_df_path(query))
        return df
