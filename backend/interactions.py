from db import interactions_col
from datetime import datetime

def log_interaction(user_id, car_id, action):
    """
    Log user interaction with a car.
    Allowed actions: view, click, booked
    """

    if action not in ["view", "click", "booked"]:
        raise ValueError("Invalid action type")

    interactions_col.insert_one({
        "user_id": user_id,
        "car_id": car_id,
        "action": action,
        "timestamp": datetime.utcnow()
    })