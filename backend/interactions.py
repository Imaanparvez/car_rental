from db import interactions_col
from datetime import datetime


# -----------------------------------
# GENERAL USER INTERACTIONS
# -----------------------------------
def log_interaction(user_id, car_id, action):

    allowed_actions = ["click", "view", "book"]

    if action not in allowed_actions:
        raise ValueError(f"Invalid interaction action: {action}")

    interactions_col.insert_one({
        "user_id": user_id,
        "car_id": car_id,
        "action": action,
        "timestamp": datetime.utcnow()
    })


# -----------------------------------
# BOOKING INTERACTION
# -----------------------------------
def log_booking_interaction(user_id, car_id):

    interactions_col.insert_one({
        "user_id": user_id,
        "car_id": car_id,
        "action": "book",
        "timestamp": datetime.utcnow()
    })