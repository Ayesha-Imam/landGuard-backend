from pymongo import MongoClient
from decouple import config

MONGO_URI = config("MONGO_URI")
DB_NAME = config("DB_NAME")

def get_mongo_collection(collection_name):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[collection_name]
