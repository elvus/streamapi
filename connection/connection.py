from pymongo import MongoClient
import os

class Connection:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_HOST'), int(os.getenv('MONGO_PORT')))
        self.db = self.client[os.getenv('MONGO_DB')]

    def get_db(self):
        return self.db
    