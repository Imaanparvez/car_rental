import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("../backend/dataset/car_rental_cbf.csv")

df.fillna("", inplace=True)

df["Mileage"] = pd.to_numeric(df["Mileage"], errors="coerce").fillna(0)
df["Engine_CC"] = pd.to_numeric(df["Engine_CC"], errors="coerce").fillna(0)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0)

for col in ["Brand", "Fuel_Type", "Body_Type"]:
    df[col] = df[col].astype(str).str.lower()

df["combined_text"] = (
    df["Brand"] + " " +
    df["Fuel_Type"] + " " +
    df["Body_Type"]
)

tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["combined_text"])

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


def recommend_cbf(prefs, top_n=5):

    user_brand = prefs.get("Brand", "").lower()

    user_text = " ".join([
        prefs.get("Brand", ""),
        prefs.get("Fuel_Type", ""),
        prefs.get("Body_Type", "")
    ]).lower()

    if not user_text.strip():
        user_text = "car"

    user_vector = tfidf.transform([user_text])
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix)[0]

    df_copy = df.copy()
    df_copy["similarity_score"] = similarity_scores

    df_copy["numeric_score"] = (
        (df_copy["Mileage"] / df_copy["Mileage"].max()) * 0.3 +
        (df_copy["Engine_CC"] / df_copy["Engine_CC"].max()) * 0.2
    )

    df_copy["final_score"] = (
        df_copy["similarity_score"] * 0.7 +
        df_copy["numeric_score"] * 0.3
    )

    df_filtered = mileage_filter(df_copy, prefs.get("Mileage"))
    df_filtered = cc_filter(df_filtered, prefs.get("Engine_CC"))

    if df_filtered.empty:
        df_filtered = df_copy

    df_filtered = df_filtered.drop_duplicates(
        subset=["Brand", "Model"]
    )

    sorted_df = df_filtered.sort_values(
        by="final_score",
        ascending=False
    )

    same_brand = sorted_df[
        sorted_df["Brand"] == user_brand
    ].head(2)

    other_brands = sorted_df[
        sorted_df["Brand"] != user_brand
    ]

    unique_rows = []
    seen_models = set(same_brand["Model"].tolist())

    for _, row in other_brands.iterrows():

        model = row["Model"]

        if model not in seen_models:
            unique_rows.append(row)
            seen_models.add(model)

        if len(unique_rows) == (top_n - len(same_brand)):
            break

    other_df = pd.DataFrame(unique_rows)

    final_df = pd.concat([same_brand, other_df])

    final_df = final_df.drop_duplicates(
        subset=["Brand", "Model"]
    )

    final_df = final_df.head(top_n)

    return final_df[[
        "Car_ID",
        "Brand",
        "Model",
        "Year",
        "Fuel_Type",
        "Body_Type",
        "Mileage",
        "Engine_CC",
        "final_score"
    ]].to_dict(orient="records")