from db import interactions_col, cars_col

def content_based_recommendations(user_id):
    recent = list(interactions_col.find({"user_id": user_id}).sort("timestamp", -1).limit(1))
    if not recent:
        return []

    car_id = recent[0]["car_id"]
    car = cars_col.find_one({"_id": car_id})

    return list(cars_col.find({"body_type": car["body_type"]}))
