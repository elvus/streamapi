from pymongo import MongoClient, ASCENDING
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
            self.create_uuid_index('catalog')
            self.create_uuid_index('viewers')
            self.create_expires_at_index('token_blacklist')
        except Exception as e:
            raise ConnectionError(f"Unable to connect to the database: {str(e)}")

    def get_db(self):
        return self.db

    def create_uuid_index(self, collection_name):
        collection = self.db[collection_name]
        indexes = collection.index_information()
        if 'uuid_1' not in indexes:
            collection.create_index([('uuid', ASCENDING)], name='uuid_1')
    
    def create_expires_at_index(self, collection_name):
        collection = self.db[collection_name]
        indexes = collection.index_information()
        if 'expires_at_1' not in indexes:
            collection.create_index([('expires_at', ASCENDING)], expireAfterSeconds=0, name='expires_at_1')
