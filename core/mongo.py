# core/mongo.py

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["website_builder_db"]  # Your DB name

# Collections
users_collection = db["users"]
websites_collection = db["websites"]
