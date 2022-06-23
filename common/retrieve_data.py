"""JGW API helpers
"""
import ast
import os
from typing import Dict, List

import pandas as pd
import requests
import six
from dashboard.models import TranslatedQuestionText, TranslatedResponseText, TranslatedText
from google.cloud import translate_v2 as translate
from jgwpandas.settings import CACHE_DIR
from pytz import country_names

FILENAMES = {
    k: os.path.join(CACHE_DIR, f"{k}.xlsx")
    for k in [
        "preferences",
        "inline",
        "messaging",
        "help_contacts",
        "contract",
        "visa",
        "joboffer",
        "beforeyougo",
    ]
}
URLS = {
    "preferences": "/preferences",
    "inline": "/inlinequestions",
    "messaging": "/messaging-questions",
    "help_contacts": "/help-contacts",
    "beforeyougo": "/beforeyougo-checklists",
    "contract": "/contract-checklists",
    "visa": "/visa-checklists",
    "joboffer": "/joboffer-checklists",
}

reversed_country_names = {v.lower(): k for k, v in country_names.items()}


client = translate.Client()


def translate_to_eng(text, client=client):
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    if isinstance(text, str):
        result = client.translate(text, target_language="en")
        return result["translatedText"]
    return text


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
        """`key` is one of: `preferences, inline, messaging, help_contacts, visa, contract, joboffer, beforeyougo`"""
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
            "origin": get_origin_country,
            "destination": get_dest_country,
        }

        def get_country_code(name):
            if name is not None:
                return reversed_country_names.get(name)
            return None

        patterns_to_replace = ["uk", "united kingdom"]
        for key in ["origin", "destination"]:
            df[key] = df["route"].apply(country_from_route[key])
            for pat in patterns_to_replace:
                df[key] = df[key].str.lower().replace(pat, country_names["GB"])
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
                return result.translation
            TranslatedQuestionText.objects.create(prismic_id=id, original_text=text)
            return text

        def translate_field_or_mark(text, field):
            models = {
                "age": TranslatedText,
                "hearAboutUs": TranslatedText,
                "gender": TranslatedText,
                "language": TranslatedText,
                "sectorOfWork": TranslatedText,
                "questionResponse": TranslatedResponseText,
            }
            TranslatedModel = models[field]
            query = TranslatedModel.objects.filter(original_text=text)
            if query.exists():
                result = query.first()
                return result.translation
            TranslatedModel.objects.create(original_text=text)
            return text

        def translate_list_field(text_list, field):
            if not isinstance(text_list, list):
                return translate_field_or_mark(text=text_list, field=field)
            return [translate_field_or_mark(text=item, field=field) for item in text_list]

        scalar_fields = ["age", "gender", "language"]
        list_fields = ["hearAboutUs", "sectorOfWork", "questionResponse"]

        df = df.fillna("")
        if "questionText" in df.columns:
            df["questionText"] = df.apply(
                lambda x: translate_question(x["questionId"], x["questionText"]), axis=1
            )
        for field in df.columns:
            if field in scalar_fields:
                df[field] = df[field].apply(lambda x: translate_field_or_mark(x, field=field))
            elif field in list_fields:
                df[field] = df[field].apply(lambda x: translate_list_field(text_list=x, field=field))
        return df
