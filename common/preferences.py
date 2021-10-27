import time
import pandas as pd
import numpy as np
from common.retrievedata import JGWApi
api = JGWApi()

class Preferences:
    def __init__(self) -> None:
        preferences = api.get_preferences()
        self.df = pd.DataFrame.from_records(preferences)

    
    def get_dataframe(self):
        return self.df
    
    def get_columns(self):
        return list(self.df.columns)

    def total_preferences(self):
        return len(self.df)

    def gender_count(self):
        genders = self.df['gender'].value_counts()
        return genders
    
    def ages(self):
        ages = self.df['age'].value_counts()
        return ages
    
    def channels(self):
        channels = self.df['hearAboutUs'].value_counts()
        return channels
