from db import cars_col

def seed_cars():
    cars = [
        {
            "brand": "Honda",
            "model": "City",
            "body_type": "Sedan",
            "price": 1200,
            "fuel_type": "Petrol",
            "transmission": "Manual / Automatic",
            "mileage": "18 km/l",
            "engine_capacity": "1498 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/honda_city.jpg"
        }
        # (Add the rest... same as your original list)
    ]

    inserted = 0
    for car in cars:
        if not cars_col.find_one({"brand": car["brand"], "model": car["model"]}):
            cars_col.insert_one(car)
            inserted += 1

    return inserted
