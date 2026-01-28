from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import login_user, register_user
from cars import get_all_cars
from interactions import log_booking_interaction
from recommendations import content_based_recommendations
from bson import ObjectId
import logging

# -----------------------------------------------------
# APP + CORS + LOGGING
# -----------------------------------------------------
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

@app.before_request
def log_request():
    print("---- NEW REQUEST ----")
    print("PATH:", request.path)
    print("BODY:", request.get_json(silent=True))


# -----------------------------------------------------
# LOGIN
# -----------------------------------------------------
@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.json
        user = login_user(data["email"], data["password"])

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Convert ObjectId
        user["_id"] = str(user["_id"])

        # Remove password (bytes cannot be JSON serialized)
        if "password" in user:
            del user["password"]

        return jsonify({"user": user}), 200

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------
# SIGNUP
# -----------------------------------------------------
@app.route("/api/signup", methods=["POST"])
def api_signup():
    try:
        data = request.json
        ok = register_user(
            data["name"], data["email"], data["phone"], data["password"]
        )
        return jsonify({"success": ok}), 200

    except Exception as e:
        print("SIGNUP ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# -----------------------------------------------------
# GET ALL CARS
# -----------------------------------------------------
@app.route("/api/cars", methods=["GET"])
def api_cars():
    cars = get_all_cars()
    for c in cars:
        c["_id"] = str(c["_id"])
    return jsonify(cars), 200


# -----------------------------------------------------
# RECOMMENDATIONS
# -----------------------------------------------------
@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    try:
        user_id = request.json["user_id"]
        result = content_based_recommendations(ObjectId(user_id))

        for r in result:
            r["_id"] = str(r["_id"])

        return jsonify(result), 200
    except Exception as e:
        print("RECOMMEND ERROR:", e)
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------
# BOOKING
# -----------------------------------------------------
@app.route("/api/book", methods=["POST"])
def api_book():
    try:
        data = request.json
        log_booking_interaction(
            ObjectId(data["user_id"]),
            ObjectId(data["car_id"])
        )
        return jsonify({"success": True}), 200
    except Exception as e:
        print("BOOK ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# -----------------------------------------------------
# ROOT CHECK
# -----------------------------------------------------
@app.route("/")
def home():
    return jsonify({"status": "Flask backend running"})


# -----------------------------------------------------
# RUN
# -----------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# RUN
# -----------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
