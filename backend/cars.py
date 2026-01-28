from db import cars_col

def get_all_cars():
    cars = list(cars_col.find())
    for c in cars:
        c["_id"] = str(c["_id"])
    return cars
