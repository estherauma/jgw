from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
QueryMap = Dict[str, list[str]]


class HelpContacts(BaseAnalytics):
    def __init__(self) -> None:
        help_contacts_data = api.get_data(key="help-contacts")
        self.df = pd.DataFrame.from_records(help_contacts_data)
        self.export_csv_name = "help_contacts_data.csv"

    def get_stats_object(self, fields: list[str] = None, filters: QueryMap = None, df=None):
        return_fields = fields or ["route", "locale", "language"]
        _df = self.get_df(filters)
        return {field: self.get_count(field, _df) for field in return_fields}
