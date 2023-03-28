from typing import Dict

import numpy as np
import pandas as pd

from common.base import BaseAnalytics
from common.retrieve_data import JGWApi, exclude_cols

api = JGWApi()
QueryMap = Dict[str, list[str]]


class Inline(BaseAnalytics):
    def __init__(self) -> None:
        inline_data, clean = api.get_data(key="inline")
        self.cleaned = clean
        self.raw_df = pd.DataFrame.from_records(inline_data)
        self.raw_df = self.raw_df.replace("", np.nan)
        self.export_csv_name = "inline_qn_responses.csv"

    def compute_stats(self, fields: list[str] = None, filters: QueryMap = None, df=None):
        _df = self.get_df(filters)
        _stats = {}
        if not _df.empty:
            return_fields = fields or [i for i in ["origin", "language", "organisation", "destination"] if i in _df.columns]
            _stats["response_count"] = len(_df)
            _stats["data"] = {field: self.count_unique(field, _df) for field in return_fields}
            questions_df = _df[[i for i in _df.columns if i not in exclude_cols]]
            if "question" in filters:
                _stats["data"]["question"] = self.count_unique(filters["question"], _df)
            else:
                _stats["data"]["question"] = questions_df.count().to_dict()
        return _stats
