from datetime import datetime
from typing import Dict

import pandas as pd
from google.cloud import bigquery

from common.base import BaseAnalytics
from common.reports import get_start_date
from common.retrieve_data import JGWApi

api = JGWApi()
client = bigquery.Client()
QueryMap = Dict[str, list[str]]
TIME_RANGE = {f"{n} Days": get_start_date(days=n, format="%Y%m%d") for n in [7, 30, 55]}


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
    def __init__(self, filters: QueryMap = None) -> None:
        self.raw_df, self.cleaned = self.get_data(filters=filters), True
        self.export_csv_name = "app_events.csv"
    
    def _get_chapters_feedback_data(self, start_date=None, end_date=None):
        chapter_feedback, clean = api.get_data(key="chapter_feedback")
        chapter_feedback_df = pd.DataFrame.from_records(chapter_feedback)
        if start_date and end_date:
            time_range = f"{start_date},{end_date}"
            chapter_feedback_df = self.filter_by_timeRange(time_range=time_range, df=chapter_feedback_df)

        new_column_names = {i.replace("ChapterOpened_", ""): v for i, v in event_to_title.items()}
        chapter_feedback_df = chapter_feedback_df.rename(columns=new_column_names)
        chapter_feedback_df = chapter_feedback_df.fillna("")
        chapter_feedback_df = chapter_feedback_df[new_column_names.values()]
        return chapter_feedback_df

    def get_data(self, filters: QueryMap = None, start=None, end=None):
        end_date = end.replace("-", "") if end else datetime.today().strftime("%Y%m%d")
        start_date = start.replace("-", "") if start else end_date
        if filters is not None and not isinstance(filters, str):
            start_date = TIME_RANGE.get(filters.get("time_range"))
        chapters_query = """
            SELECT event_name as chapters, COUNT(DISTINCT user_pseudo_id) as Users, COUNT(event_timestamp) as Count,
            FROM (SELECT * FROM `just-good-work.analytics_191478110.events_*`
                WHERE _table_suffix BETWEEN CAST({start_date} AS STRING) AND CAST({end_date} AS STRING))
            WHERE event_name LIKE 'ChapterOpened%'
            GROUP BY event_name
            """.format(
            start_date=start_date, end_date=end_date
        )
        installs = self.total_new_users()
        self.new_and_returning_users()
        chapters_df = client.query(chapters_query).to_dataframe()
        chapters_df = self.replace_chapter_names(chapters_df)
        chapters_df = chapters_df.set_index("chapters")
        if "Mark as conversion" in chapters_df.columns:
            chapters_df = chapters_df.drop(columns=["Mark as conversion"])

        chapter_feedback_df = self._get_chapters_feedback_data()
        return {"chapters": chapters_df, "chapter_feedback": chapter_feedback_df, "total_installs": installs}
    
    def total_new_users(self, start_date=None, end_date=None) -> pd.DataFrame:
        total_new_users_query = """
                SELECT COUNT(DISTINCT user_pseudo_id) as total_installs
                FROM `just-good-work.analytics_191478110.events_*`
                WHERE event_name = 'first_open'
            """
            
        if start_date is not None and end_date is not None:
            total_new_users_query += """
                AND _table_suffix BETWEEN CAST({start_date} AS STRING) AND CAST({end_date} AS STRING)
            """.format(start_date=start_date, end_date=end_date)
        
        return self.query_to_dataframe(total_new_users_query)
    
    def new_and_returning_users(self):
        new_and_returning_users_query = """
            SELECT 
            COUNT(DISTINCT CASE WHEN event_name = 'first_open' THEN user_pseudo_id END) AS new_users,
            COUNT(DISTINCT CASE WHEN event_name = 'homepage' THEN user_pseudo_id END) AS returning_users
            FROM `just-good-work.analytics_191478110.events_*`
            WHERE event_name IN ('first_open', 'homepage')
        """
        new_and_returning_users_df = self.query_to_dataframe(new_and_returning_users_query)
        return new_and_returning_users_df.iloc[0].to_dict()
    
    def query_to_dataframe(self, query):
        return client.query(query).to_dataframe()

    def replace_chapter_names(self, df) -> pd.DataFrame:
        if "Event Name" in df.columns:
            df = df.rename(columns={"Event Name": "chapters"})
        df["chapters"] = df["chapters"].replace(event_to_title)
        return df

    def get_df(self, filters: QueryMap = None) -> Dict:
        return self.get_data(filters=filters)

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None):
        data = self.get_df(filters)
        _stats = {
            "chapters": data["chapters"].to_dict(orient="index"),
            "chapter_feedback": {
                field: self.count_unique(field, data["chapter_feedback"])
                for field in data["chapter_feedback"].columns
            },
        }
        total_installs = data["total_installs"].to_dict(orient="records")[0]
        _stats.update(total_installs)
        return _stats
