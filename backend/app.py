import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId

from auth import login_user, register_user
from cars import get_all_cars
from interactions import log_booking_interaction, log_interaction
from recommender import recommend_cbf


# ------------------------------------------
# APP SETUP
# ------------------------------------------
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)


@app.before_request
def log_request():
    logging.debug("---- NEW REQUEST ----")
    logging.debug(f"PATH: {request.path}")
    logging.debug(f"BODY: {request.get_json(silent=True)}")


# ------------------------------------------
# LOGIN
# ------------------------------------------
@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        user = login_user(data.get("email"), data.get("password"))

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        user["_id"] = str(user["_id"])
        user.pop("password", None)

        return jsonify({"user": user}), 200

    except Exception as e:
        logging.exception("LOGIN ERROR")
        return jsonify({"error": str(e)}), 500


# ------------------------------------------
# SIGNUP
# ------------------------------------------
@app.route("/api/signup", methods=["POST"])
def api_signup():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False}), 400

        ok = register_user(
            data.get("name"),
            data.get("email"),
            data.get("phone"),
            data.get("password")
        )

        return jsonify({"success": ok}), 200

    except Exception as e:
        logging.exception("SIGNUP ERROR")
        return jsonify({"error": str(e)}), 500


# ------------------------------------------
# GET ALL CARS
# ------------------------------------------
@app.route("/api/cars", methods=["GET"])
def api_cars():

    try:
        cars = get_all_cars()

        for car in cars:
            car["_id"] = str(car["_id"])

        return jsonify(cars)

    except Exception as e:
        logging.exception("GET CARS ERROR")
        return jsonify({"error": str(e)}), 500


# ------------------------------------------
# RECOMMENDATIONS (FIXED ROUTE)
# ------------------------------------------
@app.route("/api/recommend", methods=["POST"])
def api_recommend():

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        results = recommend_cbf(data)

        return jsonify(results), 200

    except Exception as e:
        logging.exception("RECOMMEND ERROR")

        return jsonify({
            "error": "Recommendation failed",
            "details": str(e)
        }), 500


# ------------------------------------------
# USER INTERACTIONS
# ------------------------------------------
@app.route("/api/interact", methods=["POST"])
def api_interact():

    try:
        data = request.get_json()

        user_id = ObjectId(data["user_id"])
        car_id = ObjectId(data["car_id"])
        action = data["action"]

        log_interaction(user_id, car_id, action)

        return jsonify({"success": True})

    except Exception as e:
        logging.exception("INTERACTION ERROR")
        return jsonify({"success": False})


# ------------------------------------------
# BOOK CAR
# ------------------------------------------
@app.route("/api/book", methods=["POST"])
def api_book():

    try:
        data = request.get_json()

        log_booking_interaction(
            ObjectId(data["user_id"]),
            ObjectId(data["car_id"])
        )

        return jsonify({"success": True})

    except Exception as e:
        logging.exception("BOOK ERROR")
        return jsonify({"success": False})


# ------------------------------------------
# ROOT CHECK
# ------------------------------------------
@app.route("/")
def home():
    return jsonify({"status": "Flask backend running"})


# ------------------------------------------
# RUN SERVER
# ------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)