from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class Connection:
    def __init__(self):
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            raise ValueError("MONGO_URI environment variable is not set")

        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client.get_database()
            self.db.command("ping")
        except Exception as e:
            raise ConnectionError(f"Unable to connect to the database: {str(e)}")

    def get_db(self):
        return self.db
