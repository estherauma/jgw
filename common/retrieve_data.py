"""JGW API helpers
"""
import ast
import json
import os
from datetime import datetime
from functools import reduce
from typing import Dict, List, Tuple

import pandas as pd
import requests
from dashboard.models import JGWCache, TranslatedQuestionText, TranslatedResponseText, TranslatedText
from jgwpandas.settings import CACHE_DIR
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
CACHE_FILENAMES = {k: os.path.join(CACHE_DIR, f"{k}.csv") for k in data_categories}
vk_country_names = {v.lower(): k for k, v in country_names.items()}
vk_country_names.update({"republic of kosovo": "XK"})


class JGWApi:
    def __init__(self) -> None:
        self.base_url = os.getenv("JGW_API")
        self.session = requests.Session()

    def _get(self, url, params) -> requests.Response:
        _response = None
        _response = self.session.get(url, params=params)
        _response.raise_for_status()
        return _response

    def get_data(self, key: str) -> Tuple[list, bool]:
        """
        `key` is one of:
        `preferences, inline, messaging, help_contacts,
        visa, contract, joboffer, beforeyougo, app_events`
        """
        from dashboard.tasks import clean_data as schedule_clean_data

        data = None
        clean = False
        if key not in data_categories:
            return data, clean
        result = JGWCache.objects.filter(category=key, date_created=datetime.today().date()).first()
        if result is not None:
            clean = result.is_cleaned
            data = json.loads(result.data)
        else:
            url = f"{self.base_url}{URLS.get(key)}"
            response = self._get(url, {})
            if response and response.status_code == requests.codes.ok:
                result = response.json()
                data = result["data"]
                clean = False
                JGWCache.objects.create(category=key, data=json.dumps(data))
        if data and not clean:
            schedule_clean_data.delay(category=key)
        return data, clean

    def clean_data(self, df):
        df = self.normalise_questions_and_responses(df)
        df = self.standardise_language_names(df)
        df = self.standardise_lang_to_eng(df)
        df = self.clean_gender_data(df)
        df = self.normalise_age_bands(df)
        df = self.standardise_locations(df)
        return df

    def write_data_to_file(self, data: list, filename: str):
        df = pd.DataFrame.from_records(data)
        df.to_csv(filename, index=False)

    def get_data_from_file(self, filename) -> Dict:
        df = pd.read_csv(filename)
        data = df.to_dict(orient="records")
        return data

    def standardise_language_names(self, df):
        def get_language_name(entry):
            try:
                code = Language.get(entry).language_name()
            except LanguageTagError:
                try:
                    code = Language.find(entry).language_name()
                except (LookupError, AttributeError):
                    code = entry
            except AttributeError:
                code = entry
            return code

        if "language" in df.columns:
            df["language"] = df["language"].str.lower()
            df["language"] = df["language"].apply(get_language_name)
        return df

    def normalise_age_bands(self, df):
        groups = ["11-20", "21-30", "31-40", "41-50", "51-60", "61-70"]

        def range_str_to_int(arg):
            if isinstance(arg, str):
                temp = [i.replace("+", "") for i in arg.split("-")]
                temp = [int(i) if (i and i != "Prefer not to answer") else i for i in temp]
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
                elif len(temp) == 1 and isinstance(temp[0], int):
                    a, b = temp[0] + 1, temp[0] + 10
                elif len(temp) == 1 and isinstance(temp[0], str):
                    return temp[0], None
            return a, b

        def doer(arg):
            values = get_range_values(arg)
            if values:
                if isinstance(values[0], int):
                    arg_min, arg_max = values
                    for group in groups:
                        group_min, group_max = get_range_values(group)
                        if arg_min - group_min <= 5 and arg_max == group_max:  # arg: 35-40, group: 31-40
                            return group
                        elif arg_min == group_min and group_max - arg_max <= 5:  # arg: 31-35, group: 31-40
                            return group
                elif isinstance(values[0], str):
                    return values[0]
            return arg

        if "age" in df.columns:
            df["age"] = df["age"].apply(doer)
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
            "better not to answer": "prefer not to answer",
            "i prefer not to answer": "prefer not to answer",
            "i do not want to answer": "prefer not to answer",
            "i do not want to answer.": "prefer not to answer",
            "likes to answer": "prefer not to answer",
            "no answer": "prefer not to answer",
            "i don&#39;t want to answer": "prefer not to answer",
            "i don&#39;t want to answer.": "prefer not to answer",
            "prefer to answer": "prefer not to answer",
            "": "prefer not to answer",
            None: "prefer not to answer",
            "another": "other",
        }

        if "gender" in df.columns:
            df["gender"] = df["gender"].str.lower()
            df["gender"] = df["gender"].replace(patterns_to_replace)

        return df

    def standardise_locations(self, df):
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

        def get_country_code(name):
            if name is not None:
                code = vk_country_names.get(name)
                return name if code is None else code
            return None

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
        columns_to_replace = ["origin", "destination", "locale"]

        for key in ["origin", "destination"]:
            df[key] = df["route"].apply(country_from_route[key])
        df[columns_to_replace] = df[columns_to_replace].apply(lambda x: x.str.lower())
        df[columns_to_replace] = df[columns_to_replace].replace(patterns_to_replace)
        df[columns_to_replace] = df[columns_to_replace].apply(lambda x: x.str.title())
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
            query = TranslatedQuestionText.objects.filter(prismic_id=id).first()
            if query:
                if query.translation:
                    return query.translation
            else:
                TranslatedQuestionText.objects.create(prismic_id=id, original_text=text)
            return text

        def handle_translate(text, field):
            TranslatedModel = TranslatedResponseText if field == "questionResponse" else TranslatedText
            query = TranslatedModel.objects.filter(original_text=text).first()
            if query:
                if query.translation:
                    return query.translation
            else:
                TranslatedModel.objects.create(original_text=text)
            return text

        def translate_field_or_mark(column):
            merge_dicts = lambda x: reduce(lambda a, b: {**a, **b}, x)
            TranslatedModel = TranslatedResponseText if column.name == "questionResponse" else TranslatedText
            queryset = TranslatedModel.objects.filter(
                original_text__in=column.to_list(), translation__isnull=False
            ).values("original_text", "translation")
            if queryset:
                result_list = [{i["original_text"]: i["translation"]} for i in list(queryset)]
                result_list = merge_dicts(result_list)
                column = column.replace(result_list)
            return column

        def translate_list_field(column):
            def _do_translate_listfield(text_list, field):
                if not isinstance(text_list, list):
                    return handle_translate(text=text_list, field=field)
                TranslatedModel = TranslatedResponseText if field == "questionResponse" else TranslatedText
                queryset = TranslatedModel.objects.filter(
                    original_text__in=text_list, translation__isnull=False
                ).values("translation")
                if queryset:
                    result_list = [i["translation"] for i in list(queryset)]
                    return result_list
                return text_list

            column = column.apply(lambda x: _do_translate_listfield(text_list=x, field=column.name))
            return column

        scalar_cols = [i for i in df.columns if i in ["age", "gender", "phoneNumber", "language"]]
        list_cols = [i for i in df.columns if i in ["hearAboutUs", "sectorOfWork", "questionResponse"]]
        df = df.fillna("")
        if "questionText" in df.columns:
            df["questionText"] = df.apply(
                lambda x: translate_question(x["questionId"], x["questionText"]), axis=1
            )
        if scalar_cols:
            df[scalar_cols] = df[scalar_cols].apply(translate_field_or_mark)
        if list_cols:
            df[list_cols] = df[list_cols].apply(translate_list_field)
        return df
