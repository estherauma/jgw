from datetime import datetime
from typing import Dict

import pandas as pd
from dashboard.forms import get_start_date
from google.cloud import bigquery

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
client = bigquery.Client()
QueryMap = Dict[str, list[str]]
TIME_RANGE = {f"{n} Days": get_start_date(days=n, format="%Y%m%d") for n in [7, 30, 60, 90]}


event_to_title = {
    "ChapterOpened_1_1": "Thinking about it",
    "ChapterOpened_1_2": "Why come to work in the country",
    "ChapterOpened_1_3": "Culture and community",
    "ChapterOpened_1_4": "Type of work available",
    "ChapterOpened_1_5": "Your skills and qualifications",
    "ChapterOpened_2_1": "Application process",
    "ChapterOpened_2_10": "Agents",
    "ChapterOpened_2_11": "Travel",
    "ChapterOpened_2_12": "Immigration",
    "ChapterOpened_2_2": "Fees and charges",
    "ChapterOpened_2_3": "Equality",
    "ChapterOpened_2_4": "Immigration and visa requirements",
    "ChapterOpened_2_5": "Visa fees and costs",
    "ChapterOpened_2_6": "Contract and rights",
    "ChapterOpened_2_7": "Medical screening",
    "ChapterOpened_2_8": "Pre employment training",
    "ChapterOpened_2_9": "Your personal documents",
    "ChapterOpened_3_1": "Employment status",
    "ChapterOpened_3_10": "Universal credits and other benefits",
    "ChapterOpened_3_11": "Personal",
    "ChapterOpened_3_12": "Transport",
    "ChapterOpened_3_13": "Everyday life",
    "ChapterOpened_3_14": "Medical care",
    "ChapterOpened_3_2": "Pay",
    "ChapterOpened_3_3": "Working hours",
    "ChapterOpened_3_4": "Holidays and sick leave",
    "ChapterOpened_3_5": "Health and safety",
    "ChapterOpened_3_6": "Complaints and grievances",
    "ChapterOpened_3_7": "Resignation and dismisal",
    "ChapterOpened_3_8": "Trade Unions",
    "ChapterOpened_3_9": "Accomodation",
}


class AppEvents(BaseAnalytics):
    def __init__(self, date_range="7 Days") -> None:
        self.raw_df, self.cleaned = self.get_data(date_range=date_range), True
        self.export_csv_name = "app_events.csv"

    def get_data(self, date_range="7 Days"):
        def generate_query(date_range="7 Days", event_name=None):
            end_date = datetime.today().strftime("%Y%m%d")
            start_date = TIME_RANGE.get(date_range) or end_date
            return """
                SELECT event_name as chapters, COUNT(DISTINCT user_pseudo_id) as Users, COUNT(event_timestamp) as Count,
                FROM (SELECT * FROM `just-good-work.analytics_191478110.events_*`
                    WHERE _table_suffix BETWEEN CAST({start_date} AS STRING) AND CAST({end_date} AS STRING))
                WHERE event_name LIKE 'ChapterOpened%'
                GROUP BY event_name
                """.format(
                start_date=start_date, end_date=end_date
            )

        query = generate_query(date_range=date_range)
        df = client.query(query).to_dataframe()
        df = self.replace_chapter_names(df)
        df = df.set_index("chapters")
        if "Mark as conversion" in df.columns:
            df = df.drop(columns=["Mark as conversion"])
        return df

    def replace_chapter_names(self, df) -> pd.DataFrame:
        if "Event Name" in df.columns:
            df = df.rename(columns={"Event Name": "chapters"})
        df["chapters"] = df["chapters"].replace(event_to_title)
        return df

    def get_df(self, filters: QueryMap = None):
        df = self.get_data(date_range=filters["time_range"])
        return df

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None):
        _df = self.get_df(filters)
        _stats = {"chapters": _df.to_dict(orient="index")}
        return _stats
