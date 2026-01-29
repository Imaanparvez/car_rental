import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64

# ------------------------------------------------------------
# BACKEND URL (Render)
# ------------------------------------------------------------
BACKEND_URL = os.environ.get("BACKEND_URL")
if not BACKEND_URL:
    st.error("❌ BACKEND_URL missing in environment variables")
    st.stop()

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="AI Powered Car Rental System",
    layout="wide"
)

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"

# ------------------------------------------------------------
# BACKGROUND
# ------------------------------------------------------------
def set_background(image_path):
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: url("data:image/jpeg;base64,{encoded}") no-repeat center center fixed;
                background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

# ------------------------------------------------------------
# LOGIN PAGE
# ------------------------------------------------------------
def login_page():
    st.title("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            r = requests.post(
                f"{BACKEND_URL}/api/login",
                json={"email": email, "password": password}
            )
            data = r.json()
            if "user" in data:
                st.session_state["user"] = data["user"]
                st.session_state["page"] = "home"
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Sign Up"):
            r = requests.post(
                f"{BACKEND_URL}/api/signup",
                json={
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "password": password
                }
            )
            if r.json().get("success"):
                st.success("Account created! Please login.")
            else:
                st.error("User already exists")

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
def render_sidebar():
    st.sidebar.success(f"Welcome, {st.session_state['user']['name']} 👋")

    if st.sidebar.button("🏠 Home"):
        st.session_state["page"] = "home"
        st.rerun()

    if st.sidebar.button("📅 Book Car"):
        st.session_state["page"] = "book"
        st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state["user"] = None
        st.session_state["page"] = "login"
        st.rerun()

# ------------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------------
def home_page():
    set_background("assets/123.jpg")
    st.markdown(
        """
        <h1 style="color:white;font-size:54px;">AI Powered Car Rental System</h1>
        <p style="color:white;font-size:22px;">
        Smart. Fast. Reliable.<br>Book your perfect ride in seconds.
        </p>
        """,
        unsafe_allow_html=True
    )

# ------------------------------------------------------------
# BOOK PAGE (AI + MANUAL)
# ------------------------------------------------------------
def book_page():
    st.markdown("## 📅 Book a Car")

    # -------------------------------
    # AI RECOMMENDATION
    # -------------------------------
    with st.expander("🤖 Get AI Recommendations", expanded=True):

        c1, c2, c3 = st.columns(3)

        with c1:
            brand = st.selectbox("Brand", ["toyota", "honda", "hyundai", "bmw", "any"])
            fuel = st.selectbox("Fuel Type", ["petrol", "diesel", "electric", "any"])

        with c2:
            transmission = st.selectbox("Transmission", ["manual", "automatic", "any"])
            body_type = st.selectbox("Body Type", ["suv", "sedan", "hatchback", "any"])

        with c3:
            min_mileage = st.number_input("Min Mileage", 0, 40, 10)
            max_engine_cc = st.number_input("Max Engine CC", 800, 5000, 2500)

        if st.button("🔍 Recommend Cars"):
            payload = {
                "Brand": brand if brand != "any" else "",
                "Fuel_Type": fuel if fuel != "any" else "",
                "Transmission": transmission if transmission != "any" else "",
                "Body_Type": body_type if body_type != "any" else "",
                "min_mileage": min_mileage,
                "max_engine_cc": max_engine_cc
            }
            r = requests.post(f"{BACKEND_URL}/recommend", json=payload)
            st.session_state["recommended_cars"] = r.json()

    # -------------------------------
    # SHOW AI RESULTS
    # -------------------------------
    if "recommended_cars" in st.session_state:
        st.markdown("### ✅ AI Recommended Cars")
        for car in st.session_state["recommended_cars"]:
            cols = st.columns([4, 2, 1])
            cols[0].write(f"**{car['Brand']} {car['Model']}**")
            cols[1].write(f"Mileage: {car['Mileage']} | CC: {car['Engine_CC']}")
            if cols[2].button("Select", key=car["Car_ID"]):
                st.session_state["selected_car_from_ai"] = car

    # -------------------------------
    # FETCH ALL CARS (FALLBACK)
    # -------------------------------
    cars = requests.get(f"{BACKEND_URL}/api/cars").json()

    if "selected_car_from_ai" not in st.session_state:

        car_labels = [
            f"{c['brand']} {c['model']} ({c['body_type']})"
            for c in cars
        ]
        selected_label = st.selectbox("Select Car", car_labels)

        selected_car = next(
            c for c in cars
            if f"{c['brand']} {c['model']} ({c['body_type']})" == selected_label
        )
        price = selected_car["price"]

    else:
        selected_car = st.session_state["selected_car_from_ai"]
        st.success(f"Using AI recommended car: {selected_car['Brand']} {selected_car['Model']}")
        price = 2000  # map later from DB

    # -------------------------------
    # BOOKING DATES
    # -------------------------------
    st.markdown("### 📅 Rental Dates")
    d1, d2 = st.columns(2)

    with d1:
        pickup_date = st.date_input("Pickup Date", date.today())
    with d2:
        return_date = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((return_date - pickup_date).days, 1)
    total_cost = days * price

    st.markdown(f"## 💰 Total Cost: ₹{total_cost}")

    if st.button("Confirm Booking"):
        r = requests.post(
            f"{BACKEND_URL}/api/book",
            json={
                "user_id": st.session_state["user"]["_id"],
                "car_id": selected_car.get("_id", selected_car.get("Car_ID"))
            }
        )
        if r.json().get("success"):
            st.success("✅ Booking successful")

# ------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------
if st.session_state["user"] is None:
    login_page()
else:
    render_sidebar()
    if st.session_state["page"] == "home":
        home_page()
    elif st.session_state["page"] == "book":
        book_page()
