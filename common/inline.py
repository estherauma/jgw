import time
import pandas as pd
import numpy as np
from common.base import BaseAnalytics
from common.retrievedata import JGWApi
api = JGWApi()


class Inline(BaseAnalytics):
    def __init__(self) -> None:
        inline_data = api.get_inline_question_responses()
        self.df = pd.DataFrame.from_records(inline_data)
        self.route = self.get_route_stats()
        self.locale = self.get_locale_stats()
        self.language = self.get_language_stats()
        self.researched_employer = self.get_researched_employer_stats()
    
    def get_dataframe(self):
        return self.df
    
    def export_csv(self):
        self.df.to_csv('inline-question-response.csv')
    
    def get_data_object(self):
        data = {
            'totalResponses': self.total_items(),
            'data': {
                'route': self.route,
                'locale': self.locale,
                'language': self.language,
            }
            
            
        }
        return data

    def get_locale_stats(self):
        return self.df['locale'].value_counts().to_dict()

    def get_route_stats(self):
        return self.df['route'].value_counts().to_dict()

    def get_language_stats(self):
        return self.df['language'].value_counts().to_dict()

    def get_researched_employer_stats(self):
        return self.df['researchedEmployer'].value_counts().to_dict()
