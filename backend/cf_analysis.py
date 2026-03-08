import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------
# VISUAL SETTINGS
# -----------------------------------
plt.rcParams['figure.figsize'] = (10,6)
sns.set_style('whitegrid')

# -----------------------------------
# LOAD DATASET
# -----------------------------------
df = pd.read_csv('../backend/dataset/interactions_dataset.csv')

print("Dataset Preview")
print(df.head())

print("\nDataset Info")
print(df.info())

# -----------------------------------
# CHECK MISSING VALUES
# -----------------------------------
print("\nMissing Values")
print(df.isnull().sum())

# -----------------------------------
# ACTION DISTRIBUTION
# -----------------------------------
print("\nAction Counts")
print(df['action'].value_counts())

sns.countplot(data=df, x='action')
plt.title("Distribution of User Actions")
plt.xlabel("Action")
plt.ylabel("Count")
plt.show()

# -----------------------------------
# TOP INTERACTED CARS
# -----------------------------------
top_cars = df['car_id'].value_counts().head(10)

top_cars.plot(kind='bar')
plt.title("Top 10 Most Interacted Cars")
plt.xlabel("Car ID")
plt.ylabel("Interactions")
plt.show()

# -----------------------------------
# MOST ACTIVE USERS
# -----------------------------------
top_users = df['user_id'].value_counts().head(10)

top_users.plot(kind='bar')
plt.title("Top 10 Most Active Users")
plt.xlabel("User ID")
plt.ylabel("Interactions")
plt.show()

# -----------------------------------
# INTERACTION WEIGHTS
# -----------------------------------
weights = {
    "click": 1,
    "view": 2,
    "book": 5
}

df["interaction_score"] = df["action"].map(weights)

print("\nDataset with Interaction Score")
print(df.head())

# -----------------------------------
# USER CAR MATRIX
# -----------------------------------
user_car_matrix = df.pivot_table(
    index="user_id",
    columns="car_id",
    values="interaction_score",
    aggfunc="sum",
    fill_value=0
)

print("\nUser Car Matrix")
print(user_car_matrix.head())

# -----------------------------------
# HEATMAP VISUALIZATION
# -----------------------------------
plt.figure()
sns.heatmap(user_car_matrix, cmap="viridis")
plt.title("User-Car Interaction Heatmap")
plt.xlabel("Car ID")
plt.ylabel("User ID")
plt.show()

# -----------------------------------
# USER SIMILARITY MATRIX
# -----------------------------------
user_similarity = cosine_similarity(user_car_matrix)

user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_car_matrix.index,
    columns=user_car_matrix.index
)

print("\nUser Similarity Matrix")
print(user_similarity_df.head())

# -----------------------------------
# CF RECOMMENDER FUNCTION
# -----------------------------------
def recommend_cf(user_id, top_n=3):

    if user_id not in user_car_matrix.index:
        print("User not found")
        return []

    # similar users
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)

    # remove itself
    similar_users = similar_users.drop(user_id)

    # top similar users
    top_users = similar_users.head(5).index

    # cars already interacted
    user_cars = user_car_matrix.loc[user_id]
    user_cars = user_cars[user_cars > 0].index.tolist()

    # candidate cars
    candidate_matrix = user_car_matrix.loc[top_users]

    car_scores = candidate_matrix.mean().sort_values(ascending=False)

    recommendations = []

    for car in car_scores.index:

        # remove duplicates and already used cars
        if car not in user_cars and car not in recommendations:
            recommendations.append(car)

        if len(recommendations) == top_n:
            break

    return recommendations


# -----------------------------------
# TEST RECOMMENDER
# -----------------------------------
test_user = df["user_id"].iloc[0]

print("\nTesting CF Recommender")

recommended_cars = recommend_cf(test_user, top_n=3)

print("\nRecommended Cars:")
print(recommended_cars)