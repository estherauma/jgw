from typing import Dict
import pandas as pd
from common.app_events import AppEvents

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
        return_fields = fields or ["route", "locale", "language", "phoneNumber", "email", "organization"]
        _df = self.get_df(filters)
        app_events = AppEvents().help_contact_clicks()
        # print("app_events", app_events)
        if _df.empty:
            return {}
        return {field: self.count_unique(field, _df) for field in return_fields}
    
    def unique_help_contacts_list(self, column):
        help_contacts_df = self.get_df()
        help_contacts_series = help_contacts_df[column].str.strip()
        return help_contacts_series.unique()
    
    def total_phonenumbers_and_emails_clicks_by_org(df):
        df["organization"] = df["organization"].replace("","Not specified")
        
        phonenumber_and_emails_by_org_df = df.groupby("organization")[["phoneNumber", "email"]].agg({
            "phoneNumber": lambda phoneNumbers: phoneNumbers.count(),
            "email": lambda emails: emails.count()
        })
        return {
            "labels": phonenumber_and_emails_by_org_df.index.values,
            "phoneNumbers": phonenumber_and_emails_by_org_df["phoneNumber"].values,
            "email": phonenumber_and_emails_by_org_df["email"].values
        }
        
    def total_phonenumbers_and_emails_clicks_by_route(df):
        df["route"] = df["route"].replace("","Not specified")
        
        phonenumber_and_emails_by_route_df = df.groupby("route")[["phoneNumber", "email"]].agg({
            "phoneNumber": lambda phoneNumbers: phoneNumbers.count(),
            "email": lambda emails: emails.count()
        })
        return {
            "labels": phonenumber_and_emails_by_route_df.index.values,
            "phoneNumbers": phonenumber_and_emails_by_route_df["phoneNumber"].values,
            "email": phonenumber_and_emails_by_route_df["email"].values
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
