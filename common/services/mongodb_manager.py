import os
from pymongo.mongo_client import MongoClient
import certifi


class MongoDBConnectionManager:
    uri = os.environ.get("JGW_MONGO_CLIENT_URI")

    def __init__(self):

        client_params = {}
        if os.getenv("DEBUG") == True:
            client_params = {"tlsCAFile": certifi.where()}

        self.client = MongoClient(self.uri, **client_params)

    def get_database(self, db_name):
        return self.client[db_name]
