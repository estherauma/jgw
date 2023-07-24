import requests

class JustGoodWorkAPIClient:
    def __init__(self):
        self.base_url = 'https://sapi.justgood.work/api/v2'

    def get_data(self, endpoint):
        url = f'{self.base_url}{endpoint}'
        return self._send_get_request(url)

    def _send_get_request(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            return None