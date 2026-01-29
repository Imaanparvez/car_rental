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

    # ✅ fallback if filters too strict
    if df_filtered.empty:
        df_filtered = df_copy

    sorted_df = df_filtered.sort_values(
        "similarity_score", ascending=False
    )

    sorted_df = sorted_df.drop_duplicates(
        subset=["Brand", "Model"]
    )

    diverse = sorted_df.drop_duplicates(
        subset=["Brand"]
    )

    if len(diverse) < top_n:
        remaining = sorted_df[
            ~sorted_df.index.isin(diverse.index)
        ]
        diverse = pd.concat([diverse, remaining])

    result = diverse.head(top_n)

    return result[[
        "Car_ID", "Brand", "Model",
        "Fuel_Type", "Transmission",
        "Body_Type", "Mileage",
        "Engine_CC", "similarity_score"
    ]].to_dict(orient="records")
