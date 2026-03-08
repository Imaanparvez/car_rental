from db import cars_col
import pandas as pd


def seed_cars():

    # load dataset
    df = pd.read_csv("./dataset/car_rental_cleaned.csv")

    inserted = 0

    for _, row in df.iterrows():

        car = {
            "Brand": row["Brand"],
            "Model": row["Model"],
            "Body_Type": row["Body_Type"],
            "Fuel_Type": row["Fuel_Type"],
            "Mileage": row["Mileage"],
            "Engine_CC": row["Engine_CC"],
            "Transmission": row.get("Transmission", ""),
            "Seating_Capacity": row.get("Seating_Capacity", 5),
            "price": row.get("price", 1500),
            "image": row.get("image", "")
        }

        # prevent duplicate insert
        exists = cars_col.find_one({
            "Brand": car["Brand"],
            "Model": car["Model"]
        })

        if not exists:
            cars_col.insert_one(car)
            inserted += 1

    print(f"{inserted} cars inserted")

    return inserted


if __name__ == "__main__":
    seed_cars()