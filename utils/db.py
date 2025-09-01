from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "resume_shortlister")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["results"]

def save_result(record: dict):
    result = collection.insert_one(record)
    return str(result.inserted_id)

def get_all_results():
    results = list(collection.find({}, {"_id": 0}))
    return results