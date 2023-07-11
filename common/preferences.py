
from typing import Dict

import pandas as pd
from common.app_events import AppEvents

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi
from common.utils.dictionary_utils import convert_nested_dictionary_keys_to_uppercase

api = JGWApi()
QueryMap = Dict[str, list[str]]


def clean_df(df):
    if "organisation" in df.columns:
        df.loc[df["organisation"] == '', "organisation"] = 'Not specified'
        
        """
          The pattern matches 'Seasonal Worker Scheme' & '-' 
          & replace with an empty string
        """
        df["organisation"] = df["organisation"].replace(r'Seasonal\s+Worker\s+Scheme\s+-',"", regex=True)
    return df


class Preferences(BaseAnalytics):
    def __init__(self) -> None:
        preferences, clean = api.get_data(key="preferences")
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(preferences)
        self.export_csv_name = "preferences.csv"

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None):
        return_fields = fields or ["age", "language", "gender", "organisation"]
        
        _df = clean_df(self.get_df(filters))
        # normalize some gender 
        if _df.empty:
            return {}
        _stats = {field: self.count_unique(field, _df) for field in return_fields if field in _df.columns}
        
        _stats = convert_nested_dictionary_keys_to_uppercase(_stats)
        
        # add new and returning users to preferences stats
        # new_and_returning_users = AppEvents().new_and_returning_users()
        new_and_returning_users = {'new_users': 21868, 'returning_users': 20386}
        _stats["new_and_returning_users"]  = new_and_returning_users

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

    def unique_series_list(self, column):
        preference_df = clean_df(self.get_df())
        series = preference_df[column].str.strip()
        return series.unique()
    
    def age_groups_chart_data(self, data):
        prefer_not_to_answer = data['PREFER NOT TO ANSWER']
        del data['PREFER NOT TO ANSWER']
        sorted_items = sorted(data.items(), reverse=True)
        labels, data = zip(*sorted_items)
        labels = list(labels)
        data = list(data)
        if prefer_not_to_answer:
            labels.append('PREFER NOT TO ANSWER')
            data.append(prefer_not_to_answer)
        return {'labels': labels, 'data': data}
