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
    st.error("❌ BACKEND_URL missing")
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
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()
        st.error(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        st.error(str(e))
    return None


def safe_get(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
        st.error(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        st.error(str(e))
    return None


# ------------------------------------------------------------
# LOGIN / SIGNUP
# ------------------------------------------------------------
def login_page():
    st.title("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # LOGIN
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            data = safe_post(f"{BACKEND_URL}/api/login", {"email": email, "password": password})
            if data and "user" in data:
                st.session_state["user"] = data["user"]
                st.session_state["page"] = "book"
                st.rerun()
            else:
                st.error("Invalid credentials")

    # SIGNUP
    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Sign Up"):
            data = safe_post(f"{BACKEND_URL}/api/signup", {
                "name": name,
                "email": email,
                "phone": phone,
                "password": password
            })
            if data and data.get("success"):
                st.success("Account created! Please login.")
            else:
                st.error("Signup failed")


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
def render_sidebar():
    st.sidebar.success(f"Welcome {st.session_state['user']['name']} 👋")

    if st.sidebar.button("📅 Book Car"):
        st.session_state["page"] = "book"
        st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.rerun()


# ------------------------------------------------------------
# MAIN BOOK PAGE
# ------------------------------------------------------------
def book_page():
    st.title("🚗 Book a Car")
    st.write("### 🔍 Select Preferences")

    # -------------------------------
    # Image Tile Component
    # -------------------------------
    def tile(image_path, label, key, options):
        try:
            img_b64 = base64.b64encode(open(image_path, "rb").read()).decode()
        except:
            img_b64 = ""

        if st.button(" ", key=f"btn_{key}"):
            st.session_state[f"show_{key}"] = not st.session_state.get(f"show_{key}", False)

        st.markdown(
            f"""
            <img src="data:image/jpeg;base64,{img_b64}" 
            style="width:100%;height:120px;border-radius:12px;cursor:pointer;">
            <h5 style="text-align:center;">{label}</h5>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get(f"show_{key}", False):
            choice = st.selectbox(f"Select {label}", options, key=f"sel_{key}")
            st.session_state["filters"][key] = choice

    # 4 tiles
    t1, t2, t3, t4 = st.columns(4)

    with t1:
        tile("assets/brand.jpg", "Brand", "Brand",
             ["Toyota", "Honda", "Hyundai", "BMW"])

    with t2:
        tile("assets/fuel.jpg", "Fuel Type", "Fuel_Type",
             ["Petrol", "Diesel", "Electric"])

    with t3:
        tile("assets/body.jpg", "Body Type", "Body_Type",
             ["SUV", "Sedan", "Hatchback"])

    with t4:
        tile("assets/transmission.jpg", "Transmission", "Transmission",
             ["Manual", "Automatic"])

    st.write("---")

    # -------------------------------
    # RECOMMEND → moves to booking section
    # -------------------------------
    if st.button("📌 Recommend"):
        payload = st.session_state["filters"].copy()
        payload["min_mileage"] = 10
        payload["max_engine_cc"] = 4000

        rec = safe_post(f"{BACKEND_URL}/recommend", payload)
        if rec:
            st.session_state["recommended_cars"] = rec
            st.success("Updated recommendations!")
            st.rerun()

    # -------------------------------
    # MAIN CAR DROPDOWN
    # -------------------------------
    st.write("### 🎯 Select Your Car")

    cars = safe_get(f"{BACKEND_URL}/api/cars")
    if not cars:
        st.error("No cars in database")
        return

    dropdown = []
    rec_pairs = set()

    # Recommended cars appear FIRST
    for car in st.session_state["recommended_cars"]:
        lbl = f"{car['Brand']} {car['Model']}  (For You)"
        dropdown.append(lbl)
        rec_pairs.add((car["Brand"], car["Model"]))

    if dropdown:
        dropdown.append("────────── All Cars ──────────")

    # All cars
    for c in cars:
        if (c["brand"], c["model"]) in rec_pairs:
            continue
        dropdown.append(f"{c['brand']} {c['model']}")

    # Default selection
    default_index = 0
    if st.session_state["selected_car"]:
        sc = st.session_state["selected_car"]
        label = f"{sc['Brand']} {sc['Model']}  (For You)"
        if label in dropdown:
            default_index = dropdown.index(label)

    # Dropdown widget
    chosen = st.selectbox("Select Car", dropdown, index=default_index)

    # Map selection back to car
    if "(For You)" in chosen:
        raw = chosen.replace("  (For You)", "")
        brand, model = raw.split(" ", 1)
        selcar = next(c for c in st.session_state["recommended_cars"]
                      if c["Brand"] == brand and c["Model"] == model)
        price = 2000
    else:
        selcar = next(c for c in cars
                      if f"{c['brand']} {c['model']}" == chosen)
        price = selcar["price"]

    st.session_state["selected_car"] = selcar

    # -------------------------------
    # DATE PICKERS + PRICE
    # -------------------------------
    d1, d2 = st.columns(2)
    with d1:
        pickup = st.date_input("Pickup Date", date.today())
    with d2:
        drop = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((drop - pickup).days, 1)
    total = days * price

    st.write(f"### 💰 Total Cost: ₹{total}")

    # -------------------------------
    # CONFIRM BOOKING
    # -------------------------------
    if st.button("Confirm Booking"):
        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {"user_id": st.session_state["user"]["_id"],
             "car_id": selcar.get("_id", selcar.get("Car_ID"))}
        )
        if r and r.get("success"):
            st.success("Booking confirmed! 🎉")


# ------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------
if st.session_state["user"] is None:
    login_page()
else:
    render_sidebar()
    book_page()
