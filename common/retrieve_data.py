"""JGW API helpers
"""
import ast
import logging
import os
from time import perf_counter
from typing import Dict, List

import pandas as pd
import requests
from dashboard.models import TranslatedQuestionText, TranslatedResponseText, TranslatedText
from jgwpandas.settings import CACHE_DIR, RAW_DIR
from langcodes import Language, LanguageTagError
from pytz import country_names

data_categories = [
    "preferences",
    "inline",
    "messaging",
    "help_contacts",
    "contract",
    "visa",
    "joboffer",
    "beforeyougo",
]
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
debug_logger = logging.getLogger("djangoDebug")
CACHE_FILENAMES = {k: os.path.join(CACHE_DIR, f"{k}.csv") for k in data_categories}
RAW_FILENAMES = {k: os.path.join(RAW_DIR, f"{k}.csv") for k in data_categories}
reversed_country_names = {v.lower(): k for k, v in country_names.items()}
reversed_country_names.update({"republic of kosovo": "XK"})


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
        data = None
        filename = CACHE_FILENAMES.get(key)
        if key not in data_categories:
            return data
        try:
            data = self.get_data_from_file(filename)
        except FileNotFoundError:
            url = f"{self.base_url}{URLS.get(key)}"
            response = self._get(url, {})
            if response and response.status_code == requests.codes.ok:
                result = response.json()
                data = result["data"]
                self.write_data_to_file(data, filename)
                data = self.get_data_from_file(filename)
        return data

    def clean_data(self, df):
        debug_logger.info(f"\Started cleaning functions.")
        tic = perf_counter()
        df = self.normalise_questions_and_responses(df)
        df = self.standardise_lang_to_eng(df)
        df = self.clean_gender_data(df)
        df = self.normalise_age_bands(df)
        df = self.standardise_language_codes(df)
        df = self.swap_country_names_with_codes(df)
        toc = perf_counter()
        debug_logger.debug(f"clean_data: time elapsed: {toc-tic}")
        return df

    def write_data_to_file(self, data: list, filename: str):
        df = pd.DataFrame.from_records(data)
        df = self.clean_data(df)
        df.to_csv(filename, index=False)
        debug_logger.info(f"\nWrote df to: {filename}.")

    def get_data_from_file(self, filename) -> Dict:
        df = pd.read_csv(filename)
        data = df.to_dict(orient="records")
        debug_logger.info(f"\nRead df from: {filename}.")
        return data

    def standardise_language_codes(self, df):
        def get_language_code(entry):
            try:
                code = str(Language.get(entry))
            except LanguageTagError:
                try:
                    code = str(Language.find(entry))
                except (LookupError, AttributeError):
                    code = entry
            except AttributeError:
                code = entry
            return code

        tic = perf_counter()
        if "language" in df.columns:
            df["language"] = df["language"].str.lower()
            df["language"] = df["language"].apply(get_language_code)
        toc = perf_counter()
        debug_logger.debug(f"time elapsed: {toc-tic}")

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

        tic = perf_counter()

        if "age" in df.columns:
            df["age"] = df["age"].apply(doer)
        toc = perf_counter()
        debug_logger.debug(f"time elapsed: {toc-tic}")
        return df

    def clean_gender_data(self, df):
        patterns_to_replace = {
            "man": "male",
            "men": "male",
            "male gender": "male",
            "woman": "female",
            "women": "female",
            "feminine": "female",
            "better not answer": "prefer not to answer",
            "i prefer not to answer": "prefer not to answer",
            "i do not want to answer": "prefer not to answer",
            "i do not want to answer.": "prefer not to answer",
            "likes to answer": "prefer not to answer",
            "no answer": "prefer not to answer",
            "i don&#39;t want to answer": "prefer not to answer",
            "": "prefer not to answer",
            None: "prefer not to answer",
        }
        tic = perf_counter()
        if "gender" in df.columns:
            df["gender"] = df["gender"].str.lower()
            df["gender"] = df["gender"].replace(patterns_to_replace)
        toc = perf_counter()
        debug_logger.debug(f"time elapsed: {toc-tic}")
        return df

    def swap_country_names_with_codes(self, df):
        """Replace country name with ISO-3166-1-alpha-3 code."""

        def get_origin_country(i):
            if isinstance(i, str):
                return i.split(" -> ")[0]
            return None

        def get_dest_country(i):
            if isinstance(i, str) and i:
                return i.split(" -> ")[1]
            return None

        country_from_route = {
            "origin": get_origin_country,
            "destination": get_dest_country,
        }

        def get_country_code(column):
            def _get_country_code(name):
                if name is not None:
                    code = reversed_country_names.get(name)
                    return name if code is None else code
                return None

            column = column.apply(_get_country_code)
            return column

        patterns_to_replace = {
            "kosovo": "republic of kosovo",
            "uae": country_names["AE"].lower(),
            "bosnia and herzegovina": country_names["BA"].lower(),
            "czechia": country_names["CZ"].lower(),
            "uk": country_names["GB"].lower(),
            "united kingdom": country_names["GB"].lower(),
            "sri-lanka": country_names["LK"].lower(),
            "myanmar": country_names["MM"].lower(),
            "burma": country_names["MM"].lower(),
            "phillippines": country_names["PH"].lower(),
            "saudi": country_names["SA"].lower(),
        }
        tic = perf_counter()

        for key in ["origin", "destination"]:
            df[key] = df["route"].apply(country_from_route[key])
        df[["origin", "destination", "locale"]] = df[["origin", "destination", "locale"]].apply(
            lambda x: x.str.lower()
        )
        df[["origin", "destination", "locale"]] = df[["origin", "destination", "locale"]].replace(
            patterns_to_replace
        )
        df[["origin", "destination", "locale"]] = df[["origin", "destination", "locale"]].apply(
            get_country_code
        )
        toc = perf_counter()
        debug_logger.debug(f"time elapsed: {toc-tic}")
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

        tic = perf_counter()
        if "questionText" in df.columns:
            df["questionText"] = df["questionText"].apply(cast_to_native)
            df["questionText"] = df["questionText"].apply(unpack_question_list)

        if "questionResponse" in df.columns:
            df["questionResponse"] = df["questionResponse"].apply(cast_to_native)
            df["questionResponse"] = df["questionResponse"].apply(get_true_responses)
        toc = perf_counter()
        debug_logger.debug(f"time elapsed: {toc-tic}")
        return df

    def standardise_lang_to_eng(self, df):
        """Translate text values to English."""

        def translate_question(id, text):
            query = TranslatedQuestionText.objects.filter(prismic_id=id)
            if query.exists():
                result = query.first()
                if result.translation is not None:
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
        tic = perf_counter()

        df = df.fillna("")
        if "questionText" in df.columns:
            df["questionText"] = df.apply(
                lambda x: translate_question(x["questionId"], x["questionText"]), axis=1
            )
        df[["age", "gender", "language"]] = df[["age", "gender", "language"]].apply(
            lambda x: translate_field_or_mark(x, field=x.name)
        )
        df[["hearAboutUs", "sectorOfWork", "questionResponse"]] = df[
            ["hearAboutUs", "sectorOfWork", "questionResponse"]
        ].apply(lambda x: translate_list_field(text_list=x, field=x.name))
        toc = perf_counter()
        debug_logger.debug(f"time elapsed: {toc-tic}")
        return df
