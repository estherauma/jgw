import pandas as pd
import numpy as np

class BaseAnalytics():
    def get_df(self):
        return self.df.head(10)

    def total_items(self):
        return len(self.df)

    def get_columns(self):
        return list(self.df.columns)
