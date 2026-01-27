CAR RECOMMENDATION SYSTEM
FRONTEND – BACKEND INTEGRATION GUIDE
(Content-Based Filtering)

--------------------------------------------------
SYSTEM OVERVIEW
--------------------------------------------------

Recommender Type  : Content-Based Filtering (CBF)
Similarity Method : TF-IDF + Cosine Similarity
Numeric Filters   : Mileage, Engine_CC

Frontend collects user preferences and sends them
to the backend as JSON. Backend returns recommended
cars as JSON.

--------------------------------------------------
DATA FLOW
--------------------------------------------------

User selects preferences on website
        |
        v
Frontend sends JSON request
        |
        v
Backend computes similarity + filters
        |
        v
Backend returns JSON recommendations
        |
        v
Frontend displays car cards

--------------------------------------------------
JSON REQUEST FORMAT (FRONTEND → BACKEND)
--------------------------------------------------

REQUIRED FIELDS (Categorical – used for similarity):

{
  "Brand": "hyundai",
  "Fuel_Type": "diesel",
  "Transmission": "automatic",
  "Body_Type": "suv"
}

OPTIONAL FIELDS (Numeric – used as filters):

{
  "min_mileage": 15,
  "max_engine_cc": 2000
}

FULL EXAMPLE REQUEST:

{
  "Brand": "hyundai",
  "Fuel_Type": "diesel",
  "Transmission": "automatic",
  "Body_Type": "suv",
  "min_mileage": 15,
  "max_engine_cc": 2000
}

NOTES:
- All text values must be lowercase
- Numeric values are optional
- If numeric values are missing, backend ignores them

--------------------------------------------------
JSON RESPONSE FORMAT (BACKEND → FRONTEND)
--------------------------------------------------

Backend returns a list of recommended cars
sorted by similarity score.

EXAMPLE RESPONSE:

[
  {
    "Car_ID": 12,
    "Brand": "hyundai",
    "Model": "creta",
    "Fuel_Type": "diesel",
    "Transmission": "automatic",
    "Body_Type": "suv",
    "Mileage": 17,
    "Engine_CC": 1498,
    "similarity_score": 0.92
  },
  {
    "Car_ID": 45,
    "Brand": "kia",
    "Model": "seltos",
    "Fuel_Type": "diesel",
    "Transmission": "automatic",
    "Body_Type": "suv",
    "Mileage": 16,
    "Engine_CC": 1493,
    "similarity_score": 0.87
  }
]

--------------------------------------------------
IMAGE HANDLING (FRONTEND)
--------------------------------------------------

Dataset does NOT contain image URLs.

Recommended approaches:
1. Use body-type images (suv.jpg, sedan.jpg, etc.)
2. Use model-level images
3. Use a default fallback image

Example logic:
- If image not found → show default_car.jpg

--------------------------------------------------
FRONTEND UI REQUIREMENTS
--------------------------------------------------

Frontend should include:
- Dropdowns or radio buttons for:
  - Brand
  - Fuel Type
  - Transmission
  - Body Type

- Input fields or sliders for:
  - Minimum Mileage
  - Maximum Engine CC

- Recommendation section displaying:
  - Car Model
  - Brand
  - Fuel Type
  - Transmission
  - Mileage
  - Engine CC
  - (Optional) Similarity Score
  - Image

--------------------------------------------------
FRONTEND VALIDATION RULES
--------------------------------------------------

Before sending request:
- Ensure required categorical fields are selected
- Convert all text inputs to lowercase
- Ensure numeric values are valid numbers

--------------------------------------------------
BACKEND LOGIC SUMMARY
--------------------------------------------------

1. Convert user preferences to TF-IDF vector
2. Compute cosine similarity with car vectors
3. Apply numeric filters (Mileage, Engine_CC)
4. Rank cars by similarity score
5. Return top-N cars as JSON

--------------------------------------------------
VIVA / PANEL EXPLANATION
--------------------------------------------------

"The frontend sends user preferences as a JSON payload.
The backend applies content-based filtering using TF-IDF
and cosine similarity, applies numeric constraints, and
returns ranked recommendations in JSON format."

--------------------------------------------------
END OF FILE
--------------------------------------------------
