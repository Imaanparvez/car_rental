import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



df = pd.read_csv("../backend/dataset/car_rental_cbf.csv")

df.fillna("", inplace=True)

df["Mileage"] = pd.to_numeric(df["Mileage"], errors="coerce").fillna(0)
df["Engine_CC"] = pd.to_numeric(df["Engine_CC"], errors="coerce").fillna(0)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0)


for col in ["Brand", "Fuel_Type", "Transmission", "Body_Type"]:
    df[col] = df[col].str.lower()


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

    if prefs.get("min_mileage") is not None:
        filtered = filtered[
            filtered["Mileage"] >= prefs["min_mileage"]
        ]

    if prefs.get("max_engine_cc") is not None:
        filtered = filtered[
            filtered["Engine_CC"] <= prefs["max_engine_cc"]
        ]

    return filtered


def recommend_cbf(prefs, top_n=5):

    for key in ["Brand", "Fuel_Type", "Transmission", "Body_Type"]:
        if key in prefs and isinstance(prefs[key], str):
            prefs[key] = prefs[key].lower()


    if "min_mileage" in prefs:
        prefs["min_mileage"] = float(prefs["min_mileage"])

    if "max_engine_cc" in prefs:
        prefs["max_engine_cc"] = float(prefs["max_engine_cc"])

 
    user_text = " ".join([
        prefs.get("Brand", ""),
        prefs.get("Fuel_Type", ""),
        prefs.get("Transmission", ""),
        prefs.get("Body_Type", ""),
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
