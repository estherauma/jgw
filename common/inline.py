import time
import pandas as pd
import numpy as np
from common.retrievedata import JGWApi
api = JGWApi()


class Inline:
    def __init__(self) -> None:
        inline_data = api.get_inline_question_responses()
        self.df = pd.DataFrame.from_records(inline_data)
    
    def get_dataframe(self):
        return self.df
    
    def get_columns(self):
        return list(self.df.columns)
    
    def total_inline(self):
        return len(self.df)

