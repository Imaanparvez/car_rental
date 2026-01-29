import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# LOAD DATASET (RENDER SAFE)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "dataset", "car_rental_cbf.csv")

df = pd.read_csv(DATA_PATH)

# Normalize text
cat_cols = df.select_dtypes(include="object").columns
for col in cat_cols:
    df[col] = df[col].str.lower().str.strip()

df["feature_text"] = df[cat_cols].astype(str).agg(" ".join, axis=1)

# TF-IDF
tfidf = TfidfVectorizer()
car_tfidf_matrix = tfidf.fit_transform(df["feature_text"])


def apply_numeric_filters(df, prefs):
    if prefs.get("min_mileage") is not None:
        df = df[df["Mileage"] >= prefs["min_mileage"]]

    if prefs.get("max_engine_cc") is not None:
        df = df[df["Engine_CC"] <= prefs["max_engine_cc"]]

    return df


def recommend_cbf(prefs, top_n=5):
    user_text = (
        prefs.get("Brand", "") + " " +
        prefs.get("Fuel_Type", "") + " " +
        prefs.get("Transmission", "") + " " +
        prefs.get("Body_Type", "")
    )

    user_vector = tfidf.transform([user_text])
    scores = cosine_similarity(user_vector, car_tfidf_matrix)[0]

    df_copy = df.copy()
    df_copy["similarity_score"] = scores

    df_filtered = apply_numeric_filters(df_copy, prefs)

    result = df_filtered.sort_values(
        "similarity_score",
        ascending=False
    ).head(top_n)

    return result[[
        "Car_ID", "Brand", "Model",
        "Fuel_Type", "Transmission",
        "Body_Type", "Mileage",
        "Engine_CC", "similarity_score"
    ]].to_dict(orient="records")
