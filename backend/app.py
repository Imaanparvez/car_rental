import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
from datetime import datetime

from auth import login_user, register_user
from cars import get_all_cars
from interactions import log_booking_interaction, log_interaction
from recommender import recommend_cbf
from cf_recommender import recommend_cf
from db import interactions_col, cars_col

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)



def is_existing_user(user_id):

    count = interactions_col.count_documents({
        "user_id": ObjectId(user_id)
    })

    return count >= 3



def calculate_price(cc, days):

    base_price = 800
    multiplier = 0.8

    price_per_day = base_price + (cc * multiplier)

    total_price = price_per_day * days

    return round(total_price, 2)



@app.route("/api/login", methods=["POST"])
def api_login():

    data = request.get_json()

    user = login_user(data.get("email"), data.get("password"))

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    user["_id"] = str(user["_id"])
    user.pop("password", None)

    return jsonify({"user": user})



@app.route("/api/signup", methods=["POST"])
def api_signup():

    data = request.get_json()

    ok = register_user(
        data.get("name"),
        data.get("email"),
        data.get("phone"),
        data.get("password")
    )

    return jsonify({"success": ok})


@app.route("/api/cars", methods=["GET"])
def api_cars():

    cars = get_all_cars()

    for car in cars:
        car["_id"] = str(car["_id"])

    return jsonify(cars)



@app.route("/api/recommend", methods=["POST"])
def api_recommend():

    data = request.get_json()

    user_id = data.get("user_id")
    prefs = data.get("preferences")

    cbf_cars = recommend_cbf(prefs, top_n=3)

    cf_cars = []

    if user_id and is_existing_user(user_id):

        cf_cars = recommend_cf(ObjectId(user_id), top_n=2)

    return jsonify({
        "cbf": cbf_cars,
        "cf": cf_cars
    })



@app.route("/api/user-bookings/<user_id>", methods=["GET"])
def user_bookings(user_id):

    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(user_id),
                "action": "book"
            }
        },
        {
            "$group": {
                "_id": "$car_id",
                "count": {"$sum": 1}
            }
        }
    ]

    results = list(interactions_col.aggregate(pipeline))

    output = []

    for r in results:

        car = cars_col.find_one({"_id": r["_id"]})

        if car:

            output.append({
                "car": f"{car['Brand']} {car['Model']}",
                "count": r["count"]
            })

    return jsonify(output)



@app.route("/api/interact", methods=["POST"])
def api_interact():

    data = request.get_json()

    action = data.get("action")
    user_id = data.get("user_id")
    car_id = data.get("car_id")

    doc = {
        "user_id": ObjectId(user_id),
        "action": action,
        "timestamp": datetime.utcnow()
    }

    
    if car_id:
        try:
            doc["car_id"] = ObjectId(car_id)
        except:
            pass

    interactions_col.insert_one(doc)

    return jsonify({"success": True})



@app.route("/api/book", methods=["POST"])
def api_book():

    try:

        data = request.get_json()

        user_id = data.get("user_id")
        car_id = data.get("car_id")

        interactions_col.insert_one({
            "user_id": ObjectId(user_id),
            "car_id": ObjectId(car_id),
            "action": "book",
            "timestamp": datetime.utcnow()
        })

        return jsonify({"success": True})

    except Exception as e:

        print("BOOK ERROR:", e)

        return jsonify({"success": False})



@app.route("/")
def home():
    return jsonify({"status": "Flask backend running"})



if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)