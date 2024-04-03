import os
from pymongo.mongo_client import MongoClient
import certifi

from common.logger import KunfuPandaLogger


class MongoDBConnectionManager:
    logger = KunfuPandaLogger(log_file="logs/mongdb_connection_logger.log")
    uri = os.environ.get("JGW_MONGO_CLIENT_URI")

    def __init__(self):
        if os.getenv("DEBUG") == "False":
            client_params = {"tlsCAFile": certifi.where()}
        else:
            client_params = {}

        try:
            self.client = MongoClient(self.uri, maxPoolSize=10, connectTimeoutMS=60000, **client_params)
            self.logger.info("Successfully connected to mongoDB")
        except Exception as e:
            self.logger.error(f"Error connecting to MongoDB: {e}")

    def get_database(self, db_name):
        return self.client[db_name]
