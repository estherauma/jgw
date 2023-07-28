import pdb
from typing import Dict

import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi
from common.utils.dictionary_utils import add_prefix_to_dictionary_keys, convert_nested_dictionary_keys_to_uppercase
from common.utils.strings import camel_case_to_uppercase_text

api = JGWApi()
QueryMap = Dict[str, list[str]]


class Messaging(BaseAnalytics):
    def __init__(self) -> None:
        messaging_data, clean = api.get_data(key="messaging")
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(messaging_data)
        self.export_csv_name = "messaging_qn_responses.csv"
        

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None, df=None):
    
        _stats = {"response_count": 0, "data": {}}
        
        _df = self.get_df(filters)
        if _df.empty:
            return _stats
         
        return_fields = fields or ["origin", "destination"]
        
        _stats["response_count"] = len(_df)
        _stats["data"] = {field: self.count_unique(field, _df) for field in return_fields}
        data_with_keys_converted_to_uppercase = convert_nested_dictionary_keys_to_uppercase(_stats["data"])
        
        messaging_question_stats = add_prefix_to_dictionary_keys(
            dictionary =  data_with_keys_converted_to_uppercase,
            prefix = "messaging_question"
        )
        _stats["data"] = messaging_question_stats
    
        
        
        return _stats
