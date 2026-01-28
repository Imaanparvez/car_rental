from db import interactions_col
from datetime import datetime

def log_booking_interaction(user_id, car_id):
    # Ensure they are strings (safe for JSON + HTML)
    user_id = str(user_id)
    car_id = str(car_id)

    interactions_col.insert_one({
        "user_id": user_id,
        "car_id": car_id,
        "event": "booked",
        "timestamp": datetime.utcnow()
    })
