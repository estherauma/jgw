
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
    
    def origin_and_destination_dataframe(self):
        preference_df = clean_df(self.get_df())

        if preference_df.empty:
            return {}
    
        routes_df_series = preference_df['route']
        unique_routes = routes_df_series.unique()
        unique_routes_series = pd.Series(unique_routes)

        # split_by_arrow_get_long_and_lat
        routes_df = unique_routes_series.str.split(' -> ', expand=True)

        # add columns to then data frame
        routes_df.columns = ['Origin', 'Destination']
        routes_df = routes_df.replace('United Kingdom', 'Britain (Uk)')\
            .replace('uk', 'Britain (Uk)')\
            .replace('Other - The rest of the world', 'other').replace('uae','United Arab Emirates')\
            .replace('saudi', 'Saudi Arabia')\
            .replace('malaysia', 'Malaysia')\
            .replace('qatar', 'Qatar')
        
        routes_df = routes_df.dropna()
        routes_df.reset_index(drop=True)
        routes_df = routes_df[routes_df['Origin'] != routes_df['Destination']]
        routes_df.drop_duplicates(subset=["Origin", "Destination"], keep="first", inplace=True)
        routes_df = routes_df.reset_index(drop=True)

        return routes_df
    
    def get_destination_countries(self):
        origin_and_destination_dataframe = self.origin_and_destination_dataframe()
        destination_countries = origin_and_destination_dataframe['Destination'].dropna().unique().tolist()

        # Remove empty string from the list
        destination_countries = list(filter(None, destination_countries))

        # Create dictionary with country names as keys and values
        country_dict = {}
        for country in destination_countries:
            country_dict[country] = country

        return country_dict
    
    def origin_and_destination_list(self):
        origin_and_destination_df = self.origin_and_destination_dataframe()
        origin_and_destination_list = origin_and_destination_df.to_dict(orient='records')

        for data in origin_and_destination_list:
            data['origin_country'] = data.pop('Origin')
            data['destination_country'] = data.pop('Destination')

        return origin_and_destination_list
