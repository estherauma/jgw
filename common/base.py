import ast
import os
from typing import Dict, List

import pandas as pd
from googletrans import Translator
from jgwpandas.settings import CACHE_DIR
from pytz import country_names

QueryMap = Dict[str, str]
translator = Translator()


def get_eng_translation(text):
    t = translator.translate(text)
    return t.text


class BaseAnalytics:
    def __init__(self) -> None:
        self.export_csv_name = "export.csv"

    def export_csv(self):
        self.raw_df.to_csv(self.export_csv_name)

    def get_df_path(self, query: Dict):
        kvString_list = [f"{k}_{v}" for k, v in query.items()]
        return os.path.join(CACHE_DIR, f"{type(self).__name__}_{'-'.join(kvString_list)}.pkl")

    def get_count(self, field: str, df=None):
        _df = df.copy() if df is not None else self.raw_df.copy()
        return _df[field].value_counts().to_dict()

    def get_df(self, filters: QueryMap = None):
        _df = None

        if self.raw_df is not None:
            _df = self.raw_df.copy()

        if filters is not None:
            all_filters_path = self.get_df_path(filters)
            try:
                _df = pd.read_pickle(all_filters_path)
            except FileNotFoundError:
                for k in filters:
                    query = {k: filters[k]}
                    filter_path = self.get_df_path(query)
                    try:
                        _df = pd.read_pickle(filter_path)
                    except FileNotFoundError:
                        _df = self.filter_data(_df, query)
                _df.to_pickle(all_filters_path)
        return _df

    def swap_country_names_with_codes(self, df):
        """Replace country name with ISO-3166-1-alpha-3 code."""
        country_from_route = {
            "origin": lambda i: i.split(" -> ")[0],
            "destination": lambda i: i.split(" -> ")[1],
        }
        _ = {v.lower(): k for k, v in country_names.items()}

        def get_country_code(name):
            results = [_[key] for key in _ if name in key]
            return results[0] if len(results) else None

        for key in ["origin", "destination"]:
            df[key] = df["route"].apply(country_from_route[key])
            df[key] = df[key].apply(get_country_code)
        return df

    def standardise_lang_to_eng(self, df):
        """Translate text values to English."""
        fields_to_translate = [
            "wantToLive",
            "hearAboutUs",
            "sectorOfWork",
            "gender",
            "age",
            "language",
            "questionText",
        ]

        def translate_responses(responses: List):
            _translations = []
            if not isinstance(responses, list):
                return get_eng_translation(responses)
            for response in responses:
                _translations.append(get_eng_translation(response))
            return _translations

        # TODO: store translated question -Text, -Response to db tables to reduce repeated lookups
        if "questionResponse" in df.columns:
            df["questionResponse"] = df["questionResponse"].apply(translate_responses)

        for field in fields_to_translate:
            if field in df.columns:
                df[field] = df[field].apply(get_eng_translation)

        return df

    def normalise_questions_and_responses(self, df):
        def convert_to_native(value):
            if "[{" in value:
                return ast.literal_eval(value)
            return value

        def unpack_question_list(value):
            if isinstance(value, list):
                return value[0]
            return value

        def get_true_responses(responses: List[Dict]):
            _responses = []
            if not isinstance(responses, list):
                return responses
            for response in responses:
                if response["isChecked"] is True:
                    _responses.append(response["value"])
            return _responses

        qs = df[["questionText", "questionResponse"]]
        qs = qs.apply(convert_to_native)
        qs["questionText"] = qs["questionText"].apply(unpack_question_list)
        qs["questionResponse"] = qs["questionResponse"].apply(get_true_responses)
        df[["questionText", "questionResponse"]] = qs
        return df

    def filter_by_destination(self, destination: str, df):
        destination = destination.split(",")
        destination = [country_names.get(i).lower() for i in destination if bool(i)]
        _routes = df["route"].astype("str").str.lower()
        mask = _routes.str.endswith(tuple(destination))
        return df.loc[mask]

    def filter_by_origin(self, origin: str, df):
        origin = origin.split(",")
        origin = [country_names.get(i).lower() for i in origin if bool(i)]
        _routes = df["route"].astype("str").str.lower()
        mask = _routes.str.startswith(tuple(origin))
        return df.loc[mask]

    def filter_data(self, df, query: Dict):
        filter_map = {"destination": self.filter_by_destination, "origin": self.filter_by_origin}
        for field, value in query.items():
            filter_func = filter_map.get(field)
            if filter_func is not None:
                df = filter_func(value, df)
                df.to_pickle(self.get_df_path(query))
        return df
