from typing import Dict
import pandas as pd
from common.app_events import AppEvents
from common.lib.pandas.utils import aggregate_by_group, count_unique

from dashboard.models import TranslatedText
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
        
        emails_phonenumbers_clicks_by_route = self.emails_phonenumbers_clicks_by_group(_df)
        emails_phonenumbers_clicks_by_org = self.emails_phonenumbers_clicks_by_group(
            _df,
            group_field = "organization"
        )
        
        # print("emails_phonenumbers_clicks_by_route,", emails_phonenumbers_clicks_by_route)
        # print("-----------------------------------------------")
        # print("emails_phonenumbers_clicks_by_org::", emails_phonenumbers_clicks_by_org)
        
        print(":::", {field: self.count_unique(field, _df) for field in return_fields})
        
        if _df.empty:
            return {}
        return {field: self.count_unique(field, _df) for field in return_fields}
    
    def unique_help_contacts_list(self, column):
        help_contacts_df = self.get_df()
        help_contacts_series = help_contacts_df[column].str.strip()
        return help_contacts_series.unique()
    
    def emails_phonenumbers_clicks_by_group(
        self,
        df, 
        result_fields = ["phoneNumber", "email"],
        group_field: str = 'route'
    ):
        return aggregate_by_group(
            df,
            result_fields=result_fields,
            group_field=group_field
        )
        
    
    def phone_email_comparision(df):
        return {
            "phone": count_unique(df, "phoneNumber"),
            "email": count_unique(df, "email")
        }


def load_phone_number():
        preferences = HelpContacts()
        unique_phone_number_list = preferences.unique_help_contacts_list("phoneNumber")

        # get the existing values from the database
        existing_values = set(TranslatedText.objects.values_list('original_text', flat=True))

        new_phone_numbers = []
        for phone_number in unique_phone_number_list:
            if phone_number not in existing_values:
                new_phone_numbers.append(TranslatedText(original_text=phone_number))
        # bulk create only the new values
        TranslatedText.objects.bulk_create(new_phone_numbers)
