from db import interactions_col
from datetime import datetime

def log_booking_interaction(user_id, car_id):
    interactions_col.insert_one({
        "user_id": user_id,
        "car_id": car_id,
        "action": "booked",
        "timestamp": datetime.utcnow()
    })
