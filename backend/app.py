from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import login_user, register_user
from cars import get_all_cars
from interactions import log_booking_interaction
from recommendations import content_based_recommendations
from bson import ObjectId

app = Flask(__name__)
CORS(app)


def fix_ids(items):
    for item in items:
        item["_id"] = str(item["_id"])
    return items


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    user = login_user(data["email"], data["password"])
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    user["_id"] = str(user["_id"])
    return jsonify({"user": user}), 200


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.json
    ok = register_user(
        data["name"], data["email"], data["phone"], data["password"]
    )

    return jsonify({"success": ok}), 200


@app.route("/api/cars", methods=["GET"])
def api_cars():
    cars = get_all_cars()
    return jsonify(fix_ids(cars)), 200


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    user_id = request.json["user_id"]
    result = content_based_recommendations(ObjectId(user_id))
    return jsonify(fix_ids(result)), 200


@app.route("/api/book", methods=["POST"])
def api_book():
    data = request.json
    log_booking_interaction(
        ObjectId(data["user_id"]),
        ObjectId(data["car_id"])
    )
    return jsonify({"success": True}), 200


@app.route("/")
def home():
    return jsonify({"status": "Flask backend running"})
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
