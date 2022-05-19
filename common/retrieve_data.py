"""JGW API helpers
"""
import ast
import os
from typing import Dict, List

import pandas as pd
import requests
import six
from dashboard.models import (
    TranslatedAgeText,
    TranslatedGenderText,
    TranslatedHearAboutUsText,
    TranslatedLanguageText,
    TranslatedQuestionText,
    TranslatedResponseText,
    TranslatedSectorOfWorkText,
)
from google.cloud import translate_v2 as translate
from jgwpandas.settings import CACHE_DIR
from pytz import country_names

FILENAMES = {
    k: os.path.join(CACHE_DIR, f"{k}.xlsx") for k in ["preferences", "inline", "messaging", "help_contacts"]
}
URLS = {
    "preferences": "/preferences",
    "inline": "/inlinequestions",
    "messaging": "/messaging-questions",
    "help_contacts": "/help-contacts",
}


def get_eng_translation(text):
    client = translate.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    result = client.translate(text, target_language="en")
    return result["translatedText"]


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
                data = self.get_stats_from_file(key=key)
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

    def standardise_lang_to_eng(self, df):
        """Translate text values to English."""

        def translate_question(id, text):
            query = TranslatedQuestionText.objects.filter(prismic_id=id)
            if query.exists():
                result = query.first()
                return result.question_text
            translation = get_eng_translation(text)
            TranslatedQuestionText.objects.create(prismic_id=id, question_text=translation)
            return translation

        def translate_field(text, field):
            models = {
                "age": TranslatedAgeText,
                "hearAboutUs": TranslatedHearAboutUsText,
                "gender": TranslatedGenderText,
                "language": TranslatedLanguageText,
                "sectorOfWork": TranslatedSectorOfWorkText,
                "questionResponse": TranslatedResponseText,
            }
            TranslatedModel = models[field]
            query = TranslatedModel.objects.filter(original_text=text)
            if query.exists():
                result = query.first()
                return result.translation
            translation = get_eng_translation(text)
            TranslatedModel.objects.create(original_text=text, translation=translation)
            return translation

        def translate_list_field(text_list, field):
            if not isinstance(text_list, list):
                return translate_field(text=text_list, field=field)
            return [translate_field(text=item, field=field) for item in text_list]

        scalar_fields = ["age", "gender", "language"]
        list_fields = ["hearAboutUs", "sectorOfWork", "questionResponse"]

        df = df.fillna("")
        if "questionText" in df.columns:
            df["questionText"] = df.apply(
                lambda x: translate_question(x["questionId"], x["questionText"]), axis=1
            )
        for field in df.columns:
            if field in scalar_fields:
                df[field] = df[field].apply(lambda x: translate_field(x, field=field))
            elif field in list_fields:
                df[field] = df[field].apply(lambda x: translate_list_field(text_list=x, field=field))
        return df
