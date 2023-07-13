"""JGW API helpers
"""
import ast
import json
import os
from datetime import datetime
from functools import reduce
from typing import Dict, List, Tuple
from django.db.models import Q

import requests
from langcodes import Language, LanguageTagError
from pytz import country_names

from dashboard.models import JGWCache, TranslatedQuestionText, TranslatedResponseText, TranslatedText

data_categories = [
    "preferences",
    "inline",
    "messaging",
    "help_contacts",
    "contract",
    "visa",
    "joboffer",
    "beforeyougo",
    "chapter_feedback",
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
    "chapter_feedback": "/chapter-feedback",
}
vk_country_names = {v.lower(): k for k, v in country_names.items()}
vk_country_names.update({"republic of kosovo": "XK"})
unwanted_cols = ["", "deviceId", "undefined", "__v", "_id"]
demographic_cols = [
    "appId",
    "locale",
    "route",
    "language",
    "origin",
    "destination",
    "organisation",
    "factoryFarm",
    "createdAt",
    "updatedAt",
]
exclude_cols = [*unwanted_cols, *demographic_cols]


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
        visa, contract, joboffer, beforeyougo, app_events, chapter_feedback`
        """
        from dashboard.tasks import clean_data as schedule_clean_data

        data, clean = None, False
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
                if key == "chapter_feedback":
                    data, clean = self.transform_chapter_feedback(data)
                JGWCache.objects.create(category=key, data=json.dumps(data))
        if data and not clean:
            schedule_clean_data.delay(category=key)
        return data, clean

    def transform_chapter_feedback(self, data):
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
        fields_to_transform = {i.replace("ChapterOpened_", ""): v for i, v in event_to_title.items()}
        transform = lambda x: x["wasThisHelpful"]
        for i in data:
            for k, v in i.items():
                if k in fields_to_transform.keys():
                    i[k] = transform(v)
                else:
                    i[k] = v
        return data, True

    def clean_data(self, df):
        if df is None:
            return df
        
        df = self.normalise_questions_and_responses(df)
        df = self.standardise_language_names(df)
        df = self.standardise_lang_to_eng(df)
        df = self.clean_gender_data(df)
        df = self.normalise_age_bands(df)
        df = self.standardise_locations(df)
        df = self.clean_organisation_names(df)
        return df
    
    def clean_organisation_names(self, df):
        if "organisation" in df.columns:
            patterns_to_replace = {
                'seasonal worker scheme - agri hr':'seasonal worker scheme - agri-hr',
                'seasonal worker scheme - generic': 'seasonal worker scheme - sws generic'
            }
            df['organisation'] = df['organisation'].str.lower()
            df['organisation'] = df['organisation'].replace(patterns_to_replace)
        return df

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
        groups = ["15-17","18-20" ,"21-30", "31-40", "41-50", "51-60", "60+"]

        def range_str_to_int(arg):
            _ = ["Prefer not to answer", "prefer not to answer"]
            if isinstance(arg, str):
                temp = [i.replace("+", "") for i in arg.split("-")]
                temp = [int(i) if (i and i not in _) else i for i in temp]
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
            "a woman": "female",
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
            "i don&#39;t feel comfortable answering":"prefer not to answer",
            "behavior":"prefer not to answer"
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

            stripped_column_values = column.apply(lambda x: x.strip() if isinstance(x, str) else x)
             
            merge_dicts = lambda x: reduce(lambda a, b: {**a, **b}, x)
            TranslatedModel = TranslatedResponseText if stripped_column_values.name == "questionResponse" else TranslatedText
            queryset = TranslatedModel.objects.filter(translation__isnull=False).values("original_text", "translation")

            column_to_lowercase = stripped_column_values.apply(lambda x: x.lower() if isinstance(x, str) else x)

            if queryset:
                result_list = [{i["original_text"].lower(): i["translation"].lower()} for i in list(queryset)]
                result_list = merge_dicts(result_list)
                translated_column_mapped = column_to_lowercase.replace(result_list)
            return translated_column_mapped

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

        question_cols = [i for i in df.columns if i not in exclude_cols]
        scalar_cols = [
            i for i in df.columns if i in ["age", "gender", "phoneNumber", "language", *question_cols]
        ]
        list_cols = [i for i in df.columns if i in ["hearAboutUs", "sectorOfWork", "sectorsOfWork", "questionResponse"]]
        df = df.fillna("")
        if "questionText" in df.columns:
            df["questionText"] = df.apply(
                lambda x: translate_question(x["questionId"], x["questionText"]), axis=1
            )
        if scalar_cols:
            df[scalar_cols] = df[scalar_cols].apply(translate_field_or_mark)
        if list_cols:
            df[list_cols] = df[list_cols].apply(translate_list_field)
        columns_to_replace = [i for i in df.columns if i in question_cols]
        patterns_to_replace = {"not": "no", "it is": "yes", "are not": "no", "have": "yes"}
        if columns_to_replace:
            df[columns_to_replace] = df[columns_to_replace].apply(lambda x: x.str.lower() if isinstance(x, str) else x)
            df[columns_to_replace] = df[columns_to_replace].replace(patterns_to_replace)

        return df
