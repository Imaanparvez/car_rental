import pandas as pd
from bson import ObjectId
from db import interactions_col, cars_col
from cf_recommender import recommend_cf

# 1. Find a user that has > 3 interactions
user_interactions = list(interactions_col.aggregate([
    {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gte": 3}}},
    {"$limit": 1}
]))

if not user_interactions:
    print("No users found with >= 3 interactions. We cannot test CF.")
    exit(0)

user_id = user_interactions[0]["_id"]
print(f"Testing CF for user_id: {user_id}")

# 2. Call the recommend_cf directly
cf_cars = recommend_cf(user_id, top_n=2)
print("\nReturned CF Cars:")
for car in cf_cars:
    print(car.get("Brand"), car.get("Model"), "-", car.get("reason"))
