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
        },
        {
            "brand": "Hyundai",
            "model": "Verna",
            "body_type": "Sedan",
            "price": 1250,
            "fuel_type": "Petrol",
            "transmission": "Manual / Automatic",
            "mileage": "20 km/l",
            "engine_capacity": "1497 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/verna.jpg"
        },
        {
            "brand": "Skoda",
            "model": "Slavia",
            "body_type": "Sedan",
            "price": 1300,
            "fuel_type": "Petrol",
            "transmission": "Manual / Automatic",
            "mileage": "19 km/l",
            "engine_capacity": "1498 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/slavia.jpg"
        },

        # SUVs
        {
            "brand": "Hyundai",
            "model": "Creta",
            "body_type": "SUV",
            "price": 1500,
            "fuel_type": "Petrol / Diesel",
            "transmission": "Manual / Automatic",
            "mileage": "17 km/l",
            "engine_capacity": "1497 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/creta.jpg"
        },
        {
            "brand": "Kia",
            "model": "Seltos",
            "body_type": "SUV",
            "price": 1550,
            "fuel_type": "Petrol / Diesel",
            "transmission": "Manual / Automatic",
            "mileage": "16 km/l",
            "engine_capacity": "1497 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/seltos.jpg"
        },
        {
            "brand": "Mahindra",
            "model": "XUV700",
            "body_type": "SUV",
            "price": 1800,
            "fuel_type": "Petrol / Diesel",
            "transmission": "Manual / Automatic",
            "mileage": "15 km/l",
            "engine_capacity": "1999 cc",
            "seating_capacity": 7,
            "image": "assets/car_images/xuv700.jpg"
        },

        # Hatchbacks
        {
            "brand": "Maruti Suzuki",
            "model": "Baleno",
            "body_type": "Hatchback",
            "price": 800,
            "fuel_type": "Petrol",
            "transmission": "Manual / Automatic",
            "mileage": "22 km/l",
            "engine_capacity": "1197 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/baleno.jpg"
        },
        {
            "brand": "Hyundai",
            "model": "i20",
            "body_type": "Hatchback",
            "price": 850,
            "fuel_type": "Petrol",
            "transmission": "Manual / Automatic",
            "mileage": "20 km/l",
            "engine_capacity": "1197 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/i20.jpg"
        },
        {
            "brand": "Tata",
            "model": "Altroz",
            "body_type": "Hatchback",
            "price": 820,
            "fuel_type": "Petrol / Diesel",
            "transmission": "Manual",
            "mileage": "23 km/l",
            "engine_capacity": "1199 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/altroz.jpg"
        },

        # Small Cars
        {
            "brand": "Maruti Suzuki",
            "model": "Alto K10",
            "body_type": "Small Car",
            "price": 500,
            "fuel_type": "Petrol",
            "transmission": "Manual / Automatic",
            "mileage": "24 km/l",
            "engine_capacity": "998 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/alto_k10.jpg"
        },
        {
            "brand": "Maruti Suzuki",
            "model": "S-Presso",
            "body_type": "Small Car",
            "price": 550,
            "fuel_type": "Petrol",
            "transmission": "Manual / Automatic",
            "mileage": "25 km/l",
            "engine_capacity": "998 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/spresso.jpg"
        },
        {
            "brand": "Renault",
            "model": "Kwid",
            "body_type": "Small Car",
            "price": 520,
            "fuel_type": "Petrol",
            "transmission": "Manual / Automatic",
            "mileage": "22 km/l",
            "engine_capacity": "999 cc",
            "seating_capacity": 5,
            "image": "assets/car_images/kwid.jpg"
        }
    ]

    inserted_count = 0
    for car in cars:
        exists = cars_col.find_one({
            "brand": car["brand"],
            "model": car["model"]
        })

        if not exists:
            cars_col.insert_one(car)
            inserted_count += 1

    return inserted_count
