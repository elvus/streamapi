from pymongo import MongoClient
import logging
import os

class Connection:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_HOST'), int(os.getenv('MONGO_PORT')))
        self.db = self.client[os.getenv('MONGO_DB')]
        try:
            self.client.server_info()
        except:
            raise Exception("Couldn't connect to the MongoDB")

    def get_db(self):
        return self.db
    