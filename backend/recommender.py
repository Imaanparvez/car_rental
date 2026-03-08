import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# LOAD DATASET
# -----------------------------
df = pd.read_csv("../backend/dataset/car_rental_cbf.csv")

df.fillna("", inplace=True)

# convert numeric columns
df["Mileage"] = pd.to_numeric(df["Mileage"], errors="coerce").fillna(0)
df["Engine_CC"] = pd.to_numeric(df["Engine_CC"], errors="coerce").fillna(0)

# normalize text
for col in ["Brand", "Fuel_Type", "Body_Type"]:
    df[col] = df[col].astype(str).str.lower()

# combined text
df["combined_text"] = (
    df["Brand"] + " " +
    df["Fuel_Type"] + " " +
    df["Body_Type"]
)

# -----------------------------
# TFIDF MODEL
# -----------------------------
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["combined_text"])


# -----------------------------
# MILEAGE FILTER
# -----------------------------
def mileage_filter(dataframe, category):

    if category == "Low":
        return dataframe[dataframe["Mileage"] < 15]

    if category == "Medium":
        return dataframe[
            (dataframe["Mileage"] >= 15) &
            (dataframe["Mileage"] < 22)
        ]

    if category == "High":
        return dataframe[dataframe["Mileage"] >= 22]

    return dataframe


# -----------------------------
# ENGINE FILTER
# -----------------------------
def cc_filter(dataframe, category):

    if category == "Low Power":
        return dataframe[dataframe["Engine_CC"] < 1200]

    if category == "Medium Power":
        return dataframe[
            (dataframe["Engine_CC"] >= 1200) &
            (dataframe["Engine_CC"] < 2000)
        ]

    if category == "High Power":
        return dataframe[dataframe["Engine_CC"] >= 2000]

    return dataframe


# -----------------------------
# RECOMMENDER
# -----------------------------
def recommend_cbf(prefs, top_n=5):

    user_brand = prefs.get("Brand", "").lower()

    user_text = " ".join([
        prefs.get("Brand", ""),
        prefs.get("Fuel_Type", ""),
        prefs.get("Body_Type", "")
    ]).lower()

    if not user_text.strip():
        user_text = "car"

    # similarity
    user_vector = tfidf.transform([user_text])
    scores = cosine_similarity(user_vector, tfidf_matrix)[0]

    df_copy = df.copy()
    df_copy["similarity_score"] = scores

    # apply filters
    df_filtered = mileage_filter(df_copy, prefs.get("Mileage"))
    df_filtered = cc_filter(df_filtered, prefs.get("Engine_CC"))

    if df_filtered.empty:
        df_filtered = df_copy

    # sort by similarity
    sorted_df = df_filtered.sort_values(
        by="similarity_score",
        ascending=False
    )

    # -----------------------------
    # TOP 2 SAME BRAND
    # -----------------------------
    same_brand = sorted_df[
        sorted_df["Brand"] == user_brand
    ].head(2)

    # -----------------------------
    # UNIQUE OTHER BRANDS
    # -----------------------------
    other_brands = sorted_df[
        sorted_df["Brand"] != user_brand
    ]

    unique_brand_rows = []

    seen_brands = set()

    for _, row in other_brands.iterrows():

        brand = row["Brand"]

        if brand not in seen_brands:
            unique_brand_rows.append(row)
            seen_brands.add(brand)

        if len(unique_brand_rows) == (top_n - len(same_brand)):
            break

    other_df = pd.DataFrame(unique_brand_rows)

    # -----------------------------
    # FINAL RESULT
    # -----------------------------
    final_df = pd.concat([same_brand, other_df])

    final_df = final_df.head(top_n)

    return final_df[[
        "Car_ID",
        "Brand",
        "Model",
        "Fuel_Type",
        "Body_Type",
        "Mileage",
        "Engine_CC",
        "similarity_score"
    ]].to_dict(orient="records")