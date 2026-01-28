from db import cars_col

def get_all_cars():
    return list(cars_col.find())
