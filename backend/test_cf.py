import requests
from pymongo import MongoClient
from db import interactions_col, users_col

# 1. Find a user that has > 3 interactions
user_interactions = list(interactions_col.aggregate([
    {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gte": 3}}},
    {"$limit": 1}
]))

if not user_interactions:
    print("No users found with >= 3 interactions. We cannot test CF.")
    exit(0)

user_id = str(user_interactions[0]["_id"])
print(f"Testing CF for user_id: {user_id}")

# 2. Call the recommendation API
response = requests.post("http://localhost:5000/api/recommend", json={
    "user_id": user_id,
    "preferences": {
        "Brand": "Any",
        "Fuel_Type": "Any",
        "Body_Type": "Any",
        "Mileage": "Any",
        "Engine_CC": "Any"
    }
})

data = response.json()
print("CF Recommendations:", data.get("cf"))
