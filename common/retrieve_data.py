"""JGW API helpers
"""
import ast
from cmath import e
import os
from typing import Dict, List
from langcodes import Language, LanguageTagError

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
reversed_country_names.update({"republic of kosovo": "XK"})


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
        df = self.normalise_age_bands(df)
        df = self.standardise_language_codes(df)
        df = self.standardise_lang_to_eng(df)
        df = self.clean_gender_data(df)
        df.to_excel(filename, index=False)

    def get_stats_from_file(self, key) -> Dict:
        filename = FILENAMES.get(key)
        df = pd.read_excel(filename)
        df = self.standardise_lang_to_eng(df)
        df = self.clean_gender_data(df)
        stats = df.to_dict(orient="records")
        return stats

    def standardise_language_codes(self, df):
        def get_language_code(entry):
            try:
                code = str(Language.get(entry))
            except LanguageTagError as e:
                try:
                    code = str(Language.find(entry))
                except (LookupError, AttributeError) as e:
                    code = entry
            except AttributeError:
                code = entry
            return code

        df["language"] = df["language"].str.lower()
        df["language"] = df["language"].apply(get_language_code)
        return df

    def normalise_age_bands(self, df):
        groups = ["11-20", "21-30", "31-40", "41-50", "51-60", "61-70"]

        def range_str_to_int(arg):
            if isinstance(arg, str):
                temp = [i.replace("+", "") for i in arg.split("-")]
                temp = [int(i) for i in temp if i]
                return temp
            return arg

        def get_range_values(arg):
            try:
                a, b = list(range_str_to_int(arg))
            except TypeError:
                return None
            except ValueError:
                temp = list(range_str_to_int(arg))
                if len(temp) == 0:
                    return None
                elif len(temp) == 1:
                    a, b = temp[0] + 1, temp[0] + 10
            return a, b

        def doer(arg):
            values = get_range_values(arg)
            if values:
                arg_min, arg_max = values
                for group in groups:
                    group_min, group_max = get_range_values(group)
                    if arg_min - group_min <= 5 and arg_max == group_max:  # arg: 35-40, group: 31-40
                        return group
                    elif arg_min == group_min and group_max - arg_max <= 5:  # arg: 31-35, group: 31-40
                        return group
            return arg

        if "age" in df.columns:
            df["age"] = df["age"].apply(doer)
        return df

    def clean_gender_data(self, df):
        patterns_to_replace = {
            "male": ["man", "male", "men", "male gender"],
            "female": ["woman", "women", "feminine"],
            "prefer not to answer": [
                "better not answer",
                "i prefer not to answer",
                "i do not want to answer",
                "i do not want to answer.",
                "likes to answer",
                "no answer",
                "i don&#39;t want to answer",
                "",
                None,
            ],
        }
        if "gender" in df.columns:
            df["gender"] = df["gender"].str.lower()
            for k, v in patterns_to_replace.items():
                df["gender"] = df["gender"].replace(v, k)
        return df

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
                code = reversed_country_names.get(name)
                return name if code is None else code
            return None

        patterns_to_replace = {
            "republic of kosovo": ["kosovo"],
            country_names["AE"].lower(): ["uae"],
            country_names["BA"].lower(): ["bosnia and herzegovina"],
            country_names["CZ"].lower(): ["czechia"],
            country_names["GB"].lower(): ["uk", "united kingdom"],
            country_names["LK"].lower(): ["sri-lanka"],
            country_names["MM"].lower(): ["myanmar", "burma"],
            country_names["PH"].lower(): ["phillippines"],
            country_names["SA"].lower(): ["saudi"],
        }
        for key in ["origin", "destination"]:
            df[key] = df["route"].apply(country_from_route[key])
        for key in ["origin", "destination", "locale"]:
            df[key] = df[key].str.lower()
            for k, v in patterns_to_replace.items():
                df[key] = df[key].replace(v, k)
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
