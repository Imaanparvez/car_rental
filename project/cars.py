from db import cars_col

def get_all_cars():
    cars = []
    for c in cars_col.find():
        c["_id"] = str(c["_id"])  # Convert ObjectId to string
        cars.append(c)
    return cars
