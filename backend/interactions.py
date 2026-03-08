from db import interactions_col
from datetime import datetime


def log_interaction(user_id, car_id=None, action="view"):

    allowed_actions = ["view", "book", "search"]

    if action not in allowed_actions:
        raise ValueError(f"Invalid interaction action: {action}")

    doc = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.utcnow()
    }

    if car_id:
        doc["car_id"] = car_id

    interactions_col.insert_one(doc)


def log_booking_interaction(user_id, car_id):

    interactions_col.insert_one({
        "user_id": user_id,
        "car_id": car_id,
        "action": "book",
        "timestamp": datetime.utcnow()
    })