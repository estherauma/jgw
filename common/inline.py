from typing import Dict

import numpy as np
import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi, exclude_cols
from common.utils.dictionary_utils import convert_nested_dictionary_keys_to_uppercase
from common.utils.strings import camel_case_to_uppercase_text

api = JGWApi()
QueryMap = Dict[str, list[str]]


class Inline(BaseAnalytics):
    def __init__(self) -> None:
        inline_data, clean = api.get_data(key="inline")
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(inline_data)
        self.raw_df = self.raw_df.replace("", np.nan)
        self.export_csv_name = "inline_qn_responses.csv"
    
    def question_stats(self, questions_df=None):
        result = {}

        for column in questions_df.columns:
            counts = questions_df[column].value_counts()
            result[column] = {'yes': int(counts.get('yes', 0)), 'no': int(counts.get('no', 0))}
        
        questions_and_answers = {camel_case_to_uppercase_text(key): value for key, value in result.items()}
            
        return questions_and_answers
        
    def overview_stats(self, filters: QueryMap = None):
        return self.compute_stats(filters=filters, fields=["origin", "language", "destination"])["data"]
        
    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None, df=None):
        _df = self.get_df(filters)
        _stats = {"response_count": 0, "data": {}}
        
        
        return_fields = fields or [i for i in ["origin", "language", "organisation", "destination"] if i in _df.columns]
        _stats["response_count"] = len(_df)
        _stats["data"] = {field: self.count_unique(field, _df) for field in return_fields}
        
        data_with_keys_converted_to_uppercase = convert_nested_dictionary_keys_to_uppercase(_stats["data"])
        
        questions_df = _df[[i for i in _df.columns if i not in exclude_cols]]
        if "question" in filters:
            _stats["data"]["question"] = self.count_unique(filters["question"], _df)
        else:
            _stats["data"]["question"] = questions_df.count().to_dict()
            
        # change question keys to upper case texts        
        questions_and_answers = self.question_stats(questions_df=questions_df)
        _stats["data"] = { 
            **data_with_keys_converted_to_uppercase, 
            "questions_and_answers": questions_and_answers
        }
        
        return _stats
