from pymongo import MongoClient
import os

# Get Mongo URI from environment safely
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ MONGO_URI environment variable is missing!")

# Create the client
client = MongoClient(MONGO_URI)

# Select the correct database
db = client["car_rental"]

# Collections
users_col = db["users"]
cars_col = db["cars"]
interactions_col = db["interactions"]
