import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64

# ------------------------------------------------------------
# BACKEND URL
# ------------------------------------------------------------
BACKEND_URL = os.environ.get("BACKEND_URL")
if not BACKEND_URL:
    st.error("❌ BACKEND_URL missing in environment variables")
    st.stop()

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="AI Car Rental", layout="wide")

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "filters" not in st.session_state:
    st.session_state["filters"] = {
        "Brand": None,
        "Fuel_Type": None,
        "Body_Type": None,
        "Transmission": None
    }

if "recommended_cars" not in st.session_state:
    st.session_state["recommended_cars"] = []

if "selected_car" not in st.session_state:
    st.session_state["selected_car"] = None


# ------------------------------------------------------------
# SAFE REQUEST HELPERS
# ------------------------------------------------------------
def safe_post(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"❌ API Error {r.status_code}")
    except Exception as e:
        st.error(str(e))
    return None


def safe_get(url):
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"❌ API Error {r.status_code}")
    except Exception as e:
        st.error(str(e))
    return None


# ------------------------------------------------------------
# LOGIN PAGE
# ------------------------------------------------------------
def login_page():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        data = safe_post(f"{BACKEND_URL}/api/login", {"email": email, "password": password})
        if data and "user" in data:
            st.session_state["user"] = data["user"]
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error("Invalid credentials")


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
def render_sidebar():
    st.sidebar.success(f"Welcome {st.session_state['user']['name']} 👋")

    if st.sidebar.button("🏠 Home"):
        st.session_state["page"] = "home"
        st.rerun()

    if st.sidebar.button("🤖 Recommendations"):
        st.session_state["page"] = "recommendations"
        st.rerun()

    if st.sidebar.button("📅 Book Car"):
        st.session_state["page"] = "book"
        st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.rerun()


# ------------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------------
def home_page():
    st.title("🚗 AI Powered Car Rental System")
    st.write("Smart. Fast. Reliable.")


# ------------------------------------------------------------
# RECOMMENDATIONS PAGE
# ------------------------------------------------------------
def recommendations_page():
    st.title("🔍 Choose Car Type Filters")

    col1, col2, col3, col4 = st.columns(4)

    # Smaller dropdown tiles
    st.session_state["filters"]["Brand"] = col1.selectbox(
        "Brand", ["Select", "Toyota", "Honda", "Hyundai", "BMW"]
    ) if True else None

    st.session_state["filters"]["Fuel_Type"] = col2.selectbox(
        "Fuel", ["Select", "Petrol", "Diesel", "Electric"]
    )

    st.session_state["filters"]["Body_Type"] = col3.selectbox(
        "Body", ["Select", "SUV", "Sedan", "Hatchback"]
    )

    st.session_state["filters"]["Transmission"] = col4.selectbox(
        "Gearbox", ["Select", "Manual", "Automatic"]
    )

    st.write("---")
    if st.button("📌 Recommend Cars"):
        payload = {
            "Brand": None if st.session_state["filters"]["Brand"] == "Select" else st.session_state["filters"]["Brand"],
            "Fuel_Type": None if st.session_state["filters"]["Fuel_Type"] == "Select" else st.session_state["filters"]["Fuel_Type"],
            "Body_Type": None if st.session_state["filters"]["Body_Type"] == "Select" else st.session_state["filters"]["Body_Type"],
            "Transmission": None if st.session_state["filters"]["Transmission"] == "Select" else st.session_state["filters"]["Transmission"],
            "min_mileage": 10,
            "max_engine_cc": 3500
        }

        rec = safe_post(f"{BACKEND_URL}/recommend", payload)
        if rec:
            st.session_state["recommended_cars"] = rec
            st.success("Recommended cars updated!")
            st.rerun()

    st.write("### ⭐ AI Recommendations (For You)")
    for car in st.session_state["recommended_cars"]:
        with st.container():
            cols = st.columns([4, 1])
            cols[0].write(f"**{car['Brand']} {car['Model']}** — {car['Engine_CC']}cc | {car['Mileage']} kmpl")
            if cols[1].button("Select", key=f"recsel_{car['Car_ID']}"):
                st.session_state["selected_car"] = car
                st.session_state["page"] = "book"
                st.rerun()


# ------------------------------------------------------------
# BOOK PAGE
# ------------------------------------------------------------
def book_page():
    st.title("📅 Book Your Car")

    cars = safe_get(f"{BACKEND_URL}/api/cars")
    if not cars:
        st.error("No cars found")
        return

    # If a car was selected from recommendations → auto select it here
    if st.session_state["selected_car"]:
        default_label = (
            f"{st.session_state['selected_car']['Brand']} "
            f"{st.session_state['selected_car']['Model']}"
        )
    else:
        default_label = None

    car_labels = [
        f"{c['brand']} {c['model']}"
        for c in cars
    ]

    selected_label = st.selectbox(
        "Select Car", car_labels, index=car_labels.index(default_label) if default_label in car_labels else 0
    )

    selected_car = next(c for c in cars if f"{c['brand']} {c['model']}" == selected_label)
    price = selected_car["price"]

    col1, col2 = st.columns(2)
    with col1:
        pickup_date = st.date_input("Pickup Date", date.today())
    with col2:
        return_date = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((return_date - pickup_date).days, 1)
    st.write(f"### 💰 Total Cost: ₹{days * price}")

    if st.button("Confirm Booking"):
        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {"user_id": st.session_state["user"]["_id"], "car_id": selected_car["_id"]},
        )
        if r and r.get("success"):
            st.success("Booking confirmed!")


# ------------------------------------------------------------
# ROUTING
# ------------------------------------------------------------
if st.session_state["user"] is None:
    login_page()
else:
    render_sidebar()

    if st.session_state["page"] == "home":
        home_page()
    elif st.session_state["page"] == "recommendations":
        recommendations_page()
    elif st.session_state["page"] == "book":
        book_page()
