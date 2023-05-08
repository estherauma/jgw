from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
QueryMap = Dict[str, list[str]]


class HelpContacts(BaseAnalytics):
    def __init__(self) -> None:
        help_contacts_data, clean = api.get_data(key="help_contacts")
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(help_contacts_data)
        self.export_csv_name = "help_contacts_data.csv"

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None, df=None):
        return_fields = fields or ["route", "locale", "language", "phoneNumber", "email", "organization"]
        _df = self.get_df(filters)
        if _df.empty:
            return {}
        return {field: self.count_unique(field, _df) for field in return_fields}
    
    def unique_help_contacts_list(self, column):
        help_contacts_df = self.get_df()
        help_contacts_series = help_contacts_df[column].str.strip()
        return help_contacts_series.unique()
