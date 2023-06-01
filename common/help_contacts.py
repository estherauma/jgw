from typing import Dict
import pandas as pd
from common.lib.pandas.utils import df_aggregate_by_group, count_unique
from common.utils.helpers import dictionary_from_two_lists

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
        return_fields = fields or ["locale", "language", "organization"]
        _df = self.get_df(filters)
        
        # aggregate
        emails_and_phonenumbers_clicks_by_route = df_aggregate_by_group(
            _df,
            result_fields=["phoneNumber", "email"],
            group_field="route"
        )
        emails_and_phonenumbers_clicks_by_org = df_aggregate_by_group(
            _df,
            result_fields=["phoneNumber", "email"],
            group_field="organization"
        )
        phone_numbers_by_route = dictionary_from_two_lists(
            emails_and_phonenumbers_clicks_by_route.get("labels"),
            emails_and_phonenumbers_clicks_by_route.get("phoneNumber")
        )
        emails_by_route = dictionary_from_two_lists(
            emails_and_phonenumbers_clicks_by_route.get("labels"),
            emails_and_phonenumbers_clicks_by_route.get("email")
        )
        
        phone_numbers_by_org = dictionary_from_two_lists(
            emails_and_phonenumbers_clicks_by_org.get("labels"),
            emails_and_phonenumbers_clicks_by_org.get("phoneNumber")
        )
        emails_by_org = dictionary_from_two_lists(
            emails_and_phonenumbers_clicks_by_org.get("labels"),
            emails_and_phonenumbers_clicks_by_org.get("email")
        )
        aggregate_phonenumber_and_email_clicks = {
            "phone_number_clicks_by_route": phone_numbers_by_route, 
            "email_clicks_by_route": emails_by_route,
            "phone_number_clicks_by_org":phone_numbers_by_org,
            "email_clicks_by_org":emails_by_org
        }
        
        
        unique_value_counts = {field: self.count_unique(field, _df) for field in return_fields}
        
        if _df.empty:
            return {}
        return {**unique_value_counts, **aggregate_phonenumber_and_email_clicks}
    
    def unique_help_contacts_list(self, column):
        help_contacts_df = self.get_df()
        help_contacts_series = help_contacts_df[column].str.strip()
        return help_contacts_series.unique()
            
    
    def phone_email_comparision(df):
        return {
            "phone": count_unique(df, "phoneNumber"),
            "email": count_unique(df, "email")
        }