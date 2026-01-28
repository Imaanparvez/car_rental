from pymongo import MongoClient
import os

client = MongoClient(os.environ["MONGO_URI"])
db = client["car_rental"]

users_col = db["users"]
cars_col = db["cars"]
interactions_col = db["interactions"]
