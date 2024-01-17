from pymongo import MongoClient

class Connection:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['streamapp']

    def get_db(self):
        return self.db
    