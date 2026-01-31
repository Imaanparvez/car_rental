import pandas as pd
from pymongo import MongoClient

# 🔐 MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://imaanparvez1_db_user:zarek2026@zarek.l8fab8k.mongodb.net/?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Database & Collection
db = client.car_rental_db
collection = db.cars

# Read CSV
df = pd.read_csv("../backend/dataset/car_rental_cbf.csv")

# Optional cleaning
df.fillna("", inplace=True)

# Convert to dict
data = df.to_dict(orient="records")

# Insert (avoid duplicates)
if data:
    collection.insert_many(data)
    print("✅ CSV dataset inserted into MongoDB Atlas")
else:
    print("❌ CSV is empty")
