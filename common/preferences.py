import time
import pandas as pd
import numpy as np
from common.retrievedata import JGWApi
api = JGWApi()

class Preferences:
    def __init__(self) -> None:
        preferences = api.get_preferences()
        self.df = pd.DataFrame.from_records(preferences)
        self.genders = self.gender_count()
        self.ages = self.ages_count()
        # self.channels = self.channels_count()

    
    def get_dataframe(self):
        return self.df
    
    def get_columns(self):
        return list(self.df.columns)

    def total_preferences(self):
        return len(self.df)

    def gender_count(self):
        return self.df['gender'].value_counts().to_dict()
    
    def ages_count(self):
        return self.df['age'].value_counts().to_dict()
    
    def channels_count(self):
        return  self.df['hearAboutUs'].value_counts().to_dict()

    def get_data_object(self):
        data = {
            'ages': self.ages,
            # 'channels': self.channels,
            'genders': self.genders
        }
        return data
