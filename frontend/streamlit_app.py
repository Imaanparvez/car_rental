import streamlit as st
import requests
import os
from datetime import date, timedelta

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
st.set_page_config(
    page_title="AI Car Rental",
    layout="wide"
)

# ------------------------------------------------------------
# SESSION STATE INIT
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "preferences"

if "filters" not in st.session_state:
    st.session_state["filters"] = {
        "Brand": "Toyota",
        "Fuel_Type": "Petrol",
        "Body_Type": "SUV",
        "Transmission": "Manual"
    }

if "recommended_cars" not in st.session_state:
    st.session_state["recommended_cars"] = []

if "selected_car" not in st.session_state:
    st.session_state["selected_car"] = None

# ------------------------------------------------------------
# SAFE API HELPERS
# ------------------------------------------------------------
def safe_post(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=25)
        if r.status_code == 200:
            return r.json()
        st.error(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        st.error(str(e))
    return None

def safe_get(url):
    try:
        r = requests.get(url, timeout=25)
        if r.status_code == 200:
            return r.json()
        st.error(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        st.error(str(e))
    return None

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
def render_sidebar():
    st.sidebar.success(f"Welcome, {st.session_state['user']['name']} 👋")

    if st.sidebar.button("🎛 Preferences"):
        st.session_state["page"] = "preferences"
        st.rerun()

    if st.sidebar.button("📅 Book Car"):
        st.session_state["page"] = "book"
        st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.rerun()

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
            data = safe_post(
                f"{BACKEND_URL}/api/login",
                {"email": email, "password": password}
            )
            if data and "user" in data:
                st.session_state["user"] = data["user"]
                st.session_state["page"] = "preferences"
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Sign Up"):
            r = safe_post(
                f"{BACKEND_URL}/api/signup",
                {"name": name, "email": email, "phone": phone, "password": password}
            )
            if r and r.get("success"):
                st.success("Account created! Login now.")
            else:
                st.error("Signup failed")


# ------------------------------------------------------------
# PREFERENCES PAGE (FINAL VERSION)
# ------------------------------------------------------------
def preferences_page():
    st.title("🎛 Choose Your Preferences")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.image("assets/brand.jpeg", use_column_width=True)
        st.session_state["filters"]["Brand"] = st.selectbox(
            "Brand", ["Toyota", "Honda", "Hyundai", "BMW"], key="brand_dd"
        )

    with c2:
        st.image("assets/fuel.jpeg", use_column_width=True)
        st.session_state["filters"]["Fuel_Type"] = st.selectbox(
            "Fuel Type", ["Petrol", "Diesel", "Electric"], key="fuel_dd"
        )

    with c3:
        st.image("assets/type.jpeg", use_column_width=True)
        st.session_state["filters"]["Body_Type"] = st.selectbox(
            "Body Type", ["SUV", "Sedan", "Hatchback"], key="body_dd"
        )

    with c4:
        st.image("assets/transmission.jpeg", use_column_width=True)
        st.session_state["filters"]["Transmission"] = st.selectbox(
            "Transmission", ["Manual", "Automatic"], key="trans_dd"
        )

    st.write("---")

    # VALIDATE ALL FIELDS BEFORE RECOMMEND
    if st.button("📌 Recommend"):
        f = st.session_state["filters"]

        # Ensure NOTHING is missing
        for k, v in f.items():
            if v is None or v == "":
                st.error("⚠ Please select all preferences before recommending.")
                return

        # Payload ALWAYS contains valid strings
        payload = {
            "Brand": f["Brand"],
            "Fuel_Type": f["Fuel_Type"],
            "Body_Type": f["Body_Type"],
            "Transmission": f["Transmission"],
        }

        rec = safe_post(f"{BACKEND_URL}/recommend", payload)

        if rec:
            # clean invalid rows
            st.session_state["recommended_cars"] = [
                c for c in rec if c.get("Brand") and c.get("Model")
            ]
            st.session_state["page"] = "book"
            st.rerun()


# ------------------------------------------------------------
# BOOK CAR PAGE
# ------------------------------------------------------------
def book_page():
    st.title("🚗 Book Your Car")

    cars = safe_get(f"{BACKEND_URL}/api/cars")
    if not cars:
        st.error("No cars available")
        return

    st.write("### 🎯 Select a Car")

    dropdown = []
    recommended_pairs = set()

    # Recommended first
    for car in st.session_state["recommended_cars"]:
        brand = car.get("Brand")
        model = car.get("Model")
        if brand and model:
            dropdown.append(f"{brand} {model} (For You)")
            recommended_pairs.add((brand, model))

    # Add remaining cars
    for c in cars:
        if (c["brand"], c["model"]) not in recommended_pairs:
            dropdown.append(f"{c['brand']} {c['model']}")

    default_index = 0

    chosen = st.selectbox("Available Cars", dropdown, index=default_index)

    # Map chosen car
    if "(For You)" in chosen:
        raw = chosen.replace(" (For You)", "")
        brand, model = raw.split(" ", 1)
        selected_car = next(
            c for c in st.session_state["recommended_cars"]
            if c["Brand"] == brand and c["Model"] == model
        )
        price = 2000  # static for recommendations
    else:
        selected_car = next(
            c for c in cars if f"{c['brand']} {c['model']}" == chosen
        )
        price = selected_car["price"]

    st.session_state["selected_car"] = selected_car

    col1, col2 = st.columns(2)
    with col1:
        pickup = st.date_input("Pickup Date", date.today())
    with col2:
        drop = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((drop - pickup).days, 1)
    total = days * price

    st.write(f"### 💰 Total Cost: ₹{total}")

    if st.button("Confirm Booking"):
        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {
                "user_id": st.session_state["user"]["_id"],
                "car_id": selected_car.get("_id", selected_car.get("Car_ID"))
            }
        )
        if r and r.get("success"):
            st.success("Booking confirmed 🎉")


# ------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------
if st.session_state["user"] is None:
    login_page()
else:
    render_sidebar()
    if st.session_state["page"] == "preferences":
        preferences_page()
    elif st.session_state["page"] == "book":
        book_page()
