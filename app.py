import streamlit as st
from datetime import date, timedelta
from auth import login_user, register_user
from cars import get_all_cars
from interactions import log_booking_interaction
import base64
import os

# NEW IMPORT FOR SEED BUTTON
from seed_data import seed_cars

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="AI Powered Car Rental System", layout="wide")

# ------------------------------------------------------------
# BACKGROUND FUNCTION (HOME)
# ------------------------------------------------------------
def set_background(image_path):
    if not os.path.exists(image_path):
        return

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpeg;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}
        section.main > div {{
            padding-top: 0rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "home"

# ------------------------------------------------------------
# LOGIN / SIGNUP
# ------------------------------------------------------------
if st.session_state["user"] is None:
    st.title("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state["user"] = user
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
            if register_user(name, email, phone, password):
                st.success("Account created! Please login.")
            else:
                st.error("User already exists")

    st.stop()

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
st.sidebar.success(f"Welcome, {st.session_state['user']['name']} 👋")

if st.sidebar.button("🏠 Home"):
    st.session_state["page"] = "home"

if st.sidebar.button("📅 Book Car"):
    st.session_state["page"] = "book"

# ------------------------------------------------------------
# ⭐ ADMIN BUTTON: ADD INITIAL CARS (NO DUPLICATES)
# ------------------------------------------------------------
if st.session_state["user"]["email"] == "imaanparvez1@gmail.com":
    if st.sidebar.button("⚙️ Add Initial Cars"):
        inserted = seed_cars()
        st.sidebar.success(f"Added {inserted} new cars")

if st.sidebar.button("🚪 Logout"):
    st.session_state["user"] = None
    st.rerun()

# ------------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------------
if st.session_state["page"] == "home":

    set_background("assets/123.jpg")

    st.markdown(
        """
        <div style="height:100vh;display:flex;flex-direction:column;
                    justify-content:center;padding-left:60px;">
            <h1 style="color:white;font-size:54px;">
                AI Powered Car Rental System
            </h1>
            <p style="color:white;font-size:22px;max-width:520px;">
                Smart. Fast. Reliable.<br>
                Book your perfect ride in seconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------------------------------------------------
# BOOK CAR PAGE
# ------------------------------------------------------------
elif st.session_state["page"] == "book":

    cars = get_all_cars()

    # ---------- TITLE + IMAGE ----------
    title_col, image_col = st.columns([5, 1])

    with title_col:
        st.markdown("## 📅 Book a Car")

    with image_col:
        pass

    # ---------- CAR SELECTION ----------
    car_labels = [
        f"{c['brand']} {c['model']} ({c['body_type']})"
        for c in cars
    ]

    selected_label = st.selectbox("Select Car", car_labels)

    selected_car = next(
        c for c in cars
        if f"{c['brand']} {c['model']} ({c['body_type']})" == selected_label
    )

    # ---------- SAFE IMAGE ----------
    with image_col:
        image_path = selected_car.get("image")
        if image_path and os.path.exists(image_path):
            st.image(image_path, width=160)

    # ---------- CAR ATTRIBUTES ----------
    st.markdown("### 🚗 Car Details")

    colA, colB, colC = st.columns(3)

    with colA:
        st.write(f"**Brand:** {selected_car.get('brand')}")
        st.write(f"**Model:** {selected_car.get('model')}")
        st.write(f"**Body Type:** {selected_car.get('body_type')}")

    with colB:
        st.write(f"**Fuel Type:** {selected_car.get('fuel_type')}")
        st.write(f"**Transmission:** {selected_car.get('transmission')}")
        st.write(f"**Mileage:** {selected_car.get('mileage')} km/l")

    with colC:
        st.write(f"**Engine Capacity:** {selected_car.get('engine_capacity')}")
        st.write(f"**Seating Capacity:** {selected_car.get('seating_capacity')}")
        st.write(f"**Price / Day:** ₹{selected_car.get('price')}")

    # ---------- DATE SELECTION ----------
    st.markdown("### 📅 Rental Dates")
    d1, d2 = st.columns(2)
    with d1:
        pickup_date = st.date_input("Pickup Date", date.today())
    with d2:
        return_date = st.date_input("Return Date", date.today() + timedelta(days=1))

    total_days = max((return_date - pickup_date).days, 1)
    total_cost = total_days * selected_car["price"]

    st.markdown(f"## Total Cost: ₹{total_cost}")

    # ---------- CONFIRM BOOKING ----------
    if st.button("Confirm Booking"):
        log_booking_interaction(
            user_id=st.session_state["user"]["_id"],
            car_id=selected_car["_id"]
        )
        st.success("✅ Booking recorded successfully")


