from typing import Dict

import pandas as pd
from google.cloud import bigquery
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from common.base import BaseAnalytics
from common.custom_libs.pandas.utils import print_pandas_df_in_table_format
from common.reports import get_start_date
from common.retrieve_data import JGWApi
from tabulate import tabulate

from common.utils.date_utils import previous_dates
from common.utils.helpers import save_as_excel
from events.models import BigQueryChaptersData, BigQueryFirstOpenHomepageData

api = JGWApi()
client = bigquery.Client()
QueryMap = Dict[str, list[str]]
TIME_RANGE = {f"{n} Days": get_start_date(days=n, format="%Y-%m-%d") for n in [7, 30, 55]}


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

        if not chapter_feedback_df.empty:
            columns_in_new_column_names_and_chapter_feedback_df = [
                col for col in new_column_names.values() if col in chapter_feedback_df.columns
            ]
            chapter_feedback_df = chapter_feedback_df[columns_in_new_column_names_and_chapter_feedback_df]

        return chapter_feedback_df

    def bigquery_chapters_data(self, start_date=None, end_date=None):
        chapters_query = f"""
            SELECT 
                DATE(TIMESTAMP_MICROS(event_timestamp)) AS event_date,
                event_name, 
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'age') AS age,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'language') AS language,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'gender') AS gender,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'organisationSector') AS organisationSector,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'deviceId') AS deviceId,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'appId') AS appId,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'organisation') AS organisation,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'locale') AS locale,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'destinationState') AS destinationState,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'destination') AS destination,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'factoryFarm') AS factoryFarm,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'origin') AS origin,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'location_of_potential_work') AS location_of_potential_work,
                (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'route') AS route
            FROM 
                `just-good-work.analytics_191478110.events_*`
            WHERE 
                event_name LIKE 'ChapterOpened%' AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN '{start_date}' AND '{end_date}'
        """
        chapters_data_df = client.query(chapters_query).to_dataframe()
        chapters_data_dict = chapters_data_df.to_dict("records")

        return chapters_data_dict

    def bigquery_firstopen_homepage_data(self, start_date=None, end_date=None):
        bigquery_firstopen_homepage_query = f"""
                SELECT 
                    COUNT(DISTINCT user_pseudo_id) as users,
                    COUNT(event_timestamp) AS count,
                    DATE(TIMESTAMP_MICROS(event_timestamp)) AS event_date,
                    event_name,
                    event_params
                FROM 
                    (SELECT * FROM `just-good-work.analytics_191478110.events_*` WHERE DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN '{start_date}' AND '{end_date}')
                WHERE 
                    event_name in ('first_open', 'homepage')
                GROUP BY
                    event_date, event_name
            """
        bigquery_firstopen_homepage_df = client.query(bigquery_firstopen_homepage_query).to_dataframe()
        bigquery_firstopen_homepage_df_dict = bigquery_firstopen_homepage_df.to_dict("records")

        return bigquery_firstopen_homepage_df_dict

    def chapters_opened_data(self, start_date=None, end_date=None):
        chapters_data = list(
            BigQueryChaptersData.objects.filter(event_date__range=[start_date, end_date]).values(
                "chapters", "users", "count"
            )
        )

        chapters_df = pd.DataFrame(chapters_data)

        if not chapters_df.columns.empty:
            chapters_df = chapters_df.rename(
                columns={"users": "Users", "count": "Count", "chapters": "chapters"}
            )
            chapters_df["chapters"] = chapters_df["chapters"].replace(event_to_title)
            chapters_df = chapters_df.set_index("chapters")

        chapters_df = chapters_df.groupby(level=0).sum()
        if len(chapters_df.columns):
            chapters_df.sort_values(by="Count", ascending=False, inplace=True)

        return chapters_df

    def total_intalls_data(self, start_date=None, end_date=None):
        total_installs_data = BigQueryFirstOpenHomepageData.objects.filter(
            event_date__range=[start_date, end_date], event_name="first_open"
        ).aggregate(users=Coalesce(Sum("users"), Value(0)), count=Coalesce(Sum("count"), Value(0)))
        total_installs_df = pd.DataFrame({"total_installs": [total_installs_data.get("users")]})

        return total_installs_df

    def get_first_open_home_page(self, event_name, start_date=None, end_date=None):
        data = BigQueryFirstOpenHomepageData.objects.filter(
            event_date__range=[start_date, end_date], event_name=event_name
        ).values("event_date", "users")

        df = pd.DataFrame(data)

        if not df.columns.empty:
            df = df.drop_duplicates(subset="event_date")
            df["event_date"] = pd.to_datetime(df["event_date"])
            df = df.set_index("event_date")
            date_range = pd.date_range(start=start_date, end=end_date)
            df = df.reindex(date_range)
            df = df["users"].fillna(0)
            df.index = df.index.strftime("%b %d")

        return df

    def get_data(self, filters: QueryMap = None, start=None, end=None):
        end_date = end if end else previous_dates(days=1)
        start_date = start if start else end_date
        if filters is not None and not isinstance(filters, str):
            start_date = TIME_RANGE.get(filters.get("time_range"))

        # total installs data
        installs = self.total_intalls_data(start_date=start_date, end_date=end_date)

        # chapters_opened_data
        chapters_df = self.chapters_opened_data(start_date=start_date, end_date=end_date)

        # chapter_feedback_df
        chapter_feedback_df = self._get_chapters_feedback_data()

        return {"chapters": chapters_df, "chapter_feedback": chapter_feedback_df, "total_installs": installs}

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

    def bigquery_SWS_PASI_events(self, start_date=None, end_date=None):
        SWS_PASI_events_query = f"""
        SELECT 
            event_timestamp,
            user_pseudo_id,
            event_bundle_sequence_id,
            DATE(TIMESTAMP_MICROS(event_timestamp)) AS event_date,
            event_name,
            (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'age') AS age,
            (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'language') AS language,
            (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'gender') AS gender,
            (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'deviceId') AS deviceId,
            (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'appId') AS appId,
            (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'organisation') AS organisation,
            (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'locale') AS locale,
            (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'destination') AS destination,
            -- age, language, gender, deviceId, appId, organisation, destination
        FROM 
            `just-good-work.analytics_191478110.events_*`
        WHERE 
            event_name like "%PASI_SeasonalWorkerScheme_%" 
            AND 
            DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN '{start_date}' AND '{end_date}';
        """

        SWS_PASI_events_df = client.query(SWS_PASI_events_query).to_dataframe()
        SWS_PASI_events_dict = SWS_PASI_events_df.to_dict("records")

        return SWS_PASI_events_dict

    def bigquery_links_click_event(self, start_date=None, end_date=None):
        links_click_query = f"""
            SELECT
                    DATE(TIMESTAMP_MICROS(event_timestamp)) AS event_date,
                    event_name, 
                    (SELECT value.string_value FROM UNNEST(event_params) AS param WHERE param.key = 'link') AS link,
                    -- age, language, gender, organisationSector, deviceId, appId, organisation, locale, destinationState, destination
            FROM 
                `just-good-work.analytics_191478110.events_*` 
            WHERE 
                event_name in ("Sub_Chapter_link", "partner_Chapter_link", "message_link", "Emergency_help_link") 
            AND 
                DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN '{start_date}' AND '{end_date}';
        """

        links_click_event_df = client.query(links_click_query).to_dataframe()
        links_click_event_dict = links_click_event_df.to_dict("records")

        return links_click_event_dict
