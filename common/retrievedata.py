'''
    JGW API helpers
'''
import os
import requests

class JGWApi:
    def __init__(self) -> None:
        self.base_url = os.getenv('JGW_API')
        self.session = requests.Session()

    def build_url(self, url):
        return f'{self.base_url}{url}'

    def _get(self, url, params) -> requests.Response:
        return self.session.get(url, params=params)
    
    def get_preferences(self):
        url = self.build_url('/api/v2/preferences')
        response = self._get(url, {})
        
        if response.status_code == requests.codes.ok:
            result = response.json()
            preferences  = result['data']
            return preferences
        else:
            print('Error fetching preferences')
    
    def get_inline_question_responses(self):
        url = self.build_url('/api/v2/inlinequestions')
        response = self._get(url, {})
        if response.status_code == requests.codes.ok:
            result = response.json()
            inline_questions  = result['data']
            return inline_questions
        else:
            print('Error fetching inline questsions')
        
