import pandas as pd
from db import interactions_col, cars_col
from bson import ObjectId


def recommend_cf(user_id, top_n=3):

    interactions = list(interactions_col.find())

    if len(interactions) == 0:
        return []

    df = pd.DataFrame(interactions)

    if "user_id" not in df or "car_id" not in df:
        return []

    df["user_id"] = df["user_id"].astype(str)
    df["car_id"] = df["car_id"].astype(str)

    matrix = pd.crosstab(df["user_id"], df["car_id"])

    if str(user_id) not in matrix.index:
        return []

    target_vector = matrix.loc[str(user_id)]

    similarities = matrix.dot(target_vector)

    similarities = similarities.drop(str(user_id))

    similar_users = similarities.sort_values(ascending=False).head(3)

    if len(similar_users) == 0:
        return []

    recommended = {}

    for sim_user in similar_users.index:

        user_cars = matrix.loc[sim_user]

        liked_cars = user_cars[user_cars > 0].index

        for car in liked_cars:

            if car not in target_vector[target_vector > 0].index:

                if car not in recommended:
                    recommended[car] = 0

                recommended[car] += 1

    sorted_cars = sorted(
        recommended.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]

    results = []

    for car_id, count in sorted_cars:

        car = cars_col.find_one({"_id": ObjectId(car_id)})

        if not car:
            continue

        car["_id"] = str(car["_id"])

        car["reason"] = f"{count} users also liked"

        results.append(car)

    return results