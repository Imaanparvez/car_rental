import os
from pymongo import MongoClient
from dotenv import load_dotenv

print("Loading environment variables...")
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

print("MONGO_URI loaded:", MONGO_URI is not None)

try:
    print("Creating MongoDB client...")
    client = MongoClient(MONGO_URI)

    print("Pinging MongoDB server...")
    client.admin.command("ping")

    print("MongoDB connection successful")

    db = client["car_rental"]

    users_col = db["users"]
    cars_col = db["cars"]
    interactions_col = db["interactions"]

except Exception as e:
    print("MongoDB connection failed")
    print("Error details:", e)