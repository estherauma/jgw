"""JGW API helpers
"""
import ast
import os
from typing import Dict, List

import pandas as pd
import requests
from googletrans import Translator
from jgwpandas.settings import CACHE_DIR
from pytz import country_names
from dashboard.models import TranslatedQuestionText

FILENAMES = {
    k: os.path.join(CACHE_DIR, f"{k}.xlsx") for k in ["preferences", "inline", "messaging", "help_contacts"]
}
URLS = {
    "preferences": "/preferences",
    "inline": "/inlinequestions",
    "messaging": "/messaging-questions",
    "help_contacts": "/help-contacts",
}

translator = Translator()


def get_eng_translation(text):
    t = translator.translate(text)
    return t.text


def get_qn_translation(id, text):
    if TranslatedQuestionText.objects.filter(question_id=id).first().exists():
        return TranslatedQuestionText.objects.get(question_id=id).text
    return get_eng_translation(text)



def store_translations(df):
    data_list = df.to_dict(orient="records")
    object_list = [TranslatedQuestionText(**entry) for entry in data_list]
    TranslatedQuestionText.objects.bulk_create(object_list)


class JGWApi:
    def __init__(self) -> None:
        self.base_url = os.getenv("JGW_API")
        self.session = requests.Session()

    def _get(self, url, params) -> requests.Response:
        _response = None
        _response = self.session.get(url, params=params)
        _response.raise_for_status()
        return _response

    def get_data(self, key: str) -> list:
        """`key` is one of: `preferences, inline, messaging, help_contacts`"""
        if key not in FILENAMES.keys():
            return None
        data = None
        try:
            data = self.get_stats_from_file(key=key)
        except FileNotFoundError:
            url = f"{self.base_url}{URLS.get(key)}"
            response = self._get(url, {})
            if response and response.status_code == requests.codes.ok:
                result = response.json()
                data = result["data"]
                self.write_data_to_file(stats=data, key=key)
        return data

    def write_data_to_file(self, stats: list, key):
        filename = FILENAMES.get(key)
        df = pd.DataFrame.from_records(stats)
        df = self.swap_country_names_with_codes(df)
        df = self.normalise_questions_and_responses(df)
        df = self.standardise_lang_to_eng(df)
        df.to_excel(filename, index=False)

    def get_stats_from_file(self, key) -> Dict:
        filename = FILENAMES.get(key)
        df = pd.read_excel(filename)
        stats = df.to_dict(orient="records")
        return stats

    def swap_country_names_with_codes(self, df):
        """Replace country name with ISO-3166-1-alpha-3 code."""

        def get_origin_country(i):
            if isinstance(i, str):
                return i.split(" -> ")[0]
            return None

        def get_dest_country(i):
            if isinstance(i, str):
                return i.split(" -> ")[1]
            return None

        country_from_route = {
            "origin": lambda i: get_origin_country(i),
            "destination": lambda i: get_dest_country(i),
        }
        _ = {v.lower(): k for k, v in country_names.items()}

        def get_country_code(name):
            results = [_[key] for key in _ if name is not None and name in key]
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
        ]

        def translate_responses(responses: List):
            _translations = []
            if not isinstance(responses, list):
                return get_eng_translation(responses)
            for response in responses:
                _translations.append(get_eng_translation(response))
            return _translations

        if "questionText" in df.columns:
            translated_qn_df = df[["questionId", "questionText"]].copy()
            translated_qn_df["questionText"] = translated_qn_df.apply(lambda x: get_qn_translation(x["questionId"], x["questionText"]))
            translated_qn_df.rename(
                columns={"questionId": "prismic_id", "questionText": "question_text"}, inplace=True
            )
            store_translations(translated_qn_df)

        if "questionResponse" in df.columns:
            df["questionResponse"] = df["questionResponse"].apply(translate_responses)

        for field in fields_to_translate:
            if field in df.columns:
                df[field] = df[field].apply(get_eng_translation)

        return df

    def normalise_questions_and_responses(self, df):
        def cast_to_native(value):
            if "[{" in value or "[" in value:
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

        if "questionText" in df.columns:
            df["questionText"] = df["questionText"].apply(cast_to_native)
            df["questionText"] = df["questionText"].apply(unpack_question_list)

        if "questionResponse" in df.columns:
            df["questionResponse"] = df["questionResponse"].apply(cast_to_native)
            df["questionResponse"] = df["questionResponse"].apply(get_true_responses)
        return df
