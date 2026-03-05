import pandas as pd
from db import cars_col

def seed_cars(csv_path="car_rental_cbf.csv"):
    """
    Seeds cars collection using CSV file.
    Prevents duplicate entries based on brand + model.
    """

    # Read CSV
    df = pd.read_csv(csv_path)

    # Clean missing values
    df.fillna("", inplace=True)

    inserted = 0

    for _, row in df.iterrows():
        car = row.to_dict()

        # Adjust keys if your CSV columns are different
        brand = car.get("brand") or car.get("Brand")
        model = car.get("model") or car.get("Model")

        if not brand or not model:
            continue  # Skip invalid rows

        # Check for duplicates
        exists = cars_col.find_one({
            "brand": brand,
            "model": model
        })

        if not exists:
            # Normalize keys to lowercase (recommended)
            car["brand"] = brand
            car["model"] = model

            cars_col.insert_one(car)
            inserted += 1

    return inserted


if __name__ == "__main__":
    count = seed_cars()
    print(f"✅ {count} cars inserted from CSV")