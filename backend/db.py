import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["car_rental"]

users_col = db["users"]
cars_col = db["cars"]
interactions_col = db["interactions"]