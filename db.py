from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["car_rental"]

users_col = db["users"]
cars_col = db["cars"]
interactions_col = db["interactions"]
