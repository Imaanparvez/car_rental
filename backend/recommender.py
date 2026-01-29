import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


df = pd.read_csv("../backend/dataset/car_rental_cbf.csv")  


df.fillna("", inplace=True)

df["Mileage"] = pd.to_numeric(df["Mileage"], errors="coerce").fillna(0)
df["Engine_CC"] = pd.to_numeric(df["Engine_CC"], errors="coerce").fillna(0)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0)


df["combined_text"] = (
    df["Brand"] + " " +
    df["Fuel_Type"] + " " +
    df["Transmission"] + " " +
    df["Body_Type"]
)

tfidf = TfidfVectorizer(stop_words="english")
car_tfidf_matrix = tfidf.fit_transform(df["combined_text"])

def apply_numeric_filters(dataframe, prefs):
    filtered = dataframe.copy()

    if "min_mileage" in prefs:
        filtered = filtered[filtered["Mileage"] >= prefs["min_mileage"]]

    if "max_engine_cc" in prefs:
        filtered = filtered[filtered["Engine_CC"] <= prefs["max_engine_cc"]]

    return filtered


def recommend_cbf(prefs, top_n=5):
    user_text = " ".join([
        str(prefs.get("Brand", "")),
        str(prefs.get("Fuel_Type", "")),
        str(prefs.get("Transmission", "")),
        str(prefs.get("Body_Type", "")),
    ]).strip()

    if not user_text:
        user_text = "car"

    user_vector = tfidf.transform([user_text])
    scores = cosine_similarity(user_vector, car_tfidf_matrix)[0]

    df_copy = df.copy()
    df_copy["similarity_score"] = scores.astype(float)

    df_filtered = apply_numeric_filters(df_copy, prefs)
    if df_filtered.empty:
        df_filtered = df_copy

    sorted_df = df_filtered.sort_values(
        by="similarity_score",
        ascending=False
    )
    seen_brands = set()
    final_rows = []

    for _, row in sorted_df.iterrows():
        brand = row["Brand"]

        if brand not in seen_brands:
            seen_brands.add(brand)
            final_rows.append(row)

        if len(final_rows) == top_n:
            break

    if not final_rows:
        return []

    result = pd.DataFrame(final_rows)

    result = result.replace([np.inf, -np.inf], 0)
    result = result.fillna("")

    return result[[
        "Car_ID", "Brand", "Model",
        "Fuel_Type", "Transmission",
        "Body_Type", "Mileage",
        "Engine_CC", "similarity_score"
    ]].to_dict(orient="records")

