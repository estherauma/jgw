from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi

api = JGWApi()
QueryMap = Dict[str, list[str]]

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
    def __init__(self) -> None:
        # mock events data fetching pending firebase config
        app_events, clean = pd.read_csv("./events.csv"), True
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(app_events)
        self.export_csv_name = "app_events.csv"

    def replace_chapter_names(self, df) -> pd.DataFrame:
        df = df.rename({"Event Names": "chapters"})
        df["chapters"] = df["chapters"].replace(event_to_title)
        return df

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None):
        _df = self.get_df(filters)
        df = _df.set_index("chapters")
        df = df.drop("Mark as Conversion")
        _stats = df.to_dict(orient="index")
        return _stats
