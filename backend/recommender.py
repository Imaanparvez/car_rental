import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def recommend_cbf(prefs, top_n=5):
    """
    Content-Based Filtering recommendation

    prefs: dict from frontend
    top_n: number of cars to recommend
    returns: list of dicts (JSON serializable)
    """

   
 
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

   
    try:
        df_filtered = apply_numeric_filters(df_copy, prefs)
    except Exception:
        df_filtered = df_copy

   
    if df_filtered.empty:
        df_filtered = df_copy

  
    sorted_df = df_filtered.sort_values(
        by="similarity_score",
        ascending=False
    )

    # Remove exact duplicates
    sorted_df = sorted_df.drop_duplicates(
        subset=["Brand", "Model"]
    )

    # Brand diversity
    diverse = sorted_df.drop_duplicates(subset=["Brand"])

    if len(diverse) < top_n:
        remaining = sorted_df.loc[
            ~sorted_df.index.isin(diverse.index)
        ]
        diverse = pd.concat([diverse, remaining])

    result = diverse.head(top_n)

  
    output_cols = [
        "Car_ID", "Brand", "Model",
        "Fuel_Type", "Transmission",
        "Body_Type", "Mileage",
        "Engine_CC", "similarity_score"
    ]

   
    output_cols = [c for c in output_cols if c in result.columns]

    result = result[output_cols]

   
    result = result.replace([np.inf, -np.inf], 0)
    result = result.fillna("")

    return result.to_dict(orient="records")
