import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64
import json

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
st.set_page_config(page_title="AI Powered Car Rental System", layout="wide")

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"


# ------------------------------------------------------------
# BACKGROUND FUNCTION
# ------------------------------------------------------------
def set_background(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()

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
    except:
        pass


# ------------------------------------------------------------
# LOGIN PAGE
# ------------------------------------------------------------
def login_page():
    st.title("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # LOGIN TAB
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                r = requests.post(
                    f"{BACKEND_URL}/api/login",
                    json={"email": email, "password": password},
                )
                data = r.json()

                if "user" in data:
                    st.session_state["user"] = data["user"]
                    st.session_state["page"] = "home"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

            except Exception as e:
                st.error(f"Backend error: {e}")

    # SIGNUP TAB
    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Sign Up"):
            try:
                r = requests.post(
                    f"{BACKEND_URL}/api/signup",
                    json={"name": name, "email": email, "phone": phone, "password": password},
                )
                resp = r.json()

                if resp.get("success"):
                    st.success("Account created! Please login.")
                else:
                    st.error("User already exists")
            except Exception as e:
                st.error(f"Backend error: {e}")


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
# HOME PAGE (ORIGINAL DESIGN)
# ------------------------------------------------------------
def home_page():
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
# BOOKING PAGE (ORIGINAL LAYOUT)
# ------------------------------------------------------------
def book_page():

    try:
        cars = requests.get(f"{BACKEND_URL}/api/cars").json()
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        return

    title_col, image_col = st.columns([5, 1])

    with title_col:
        st.markdown("## 📅 Book a Car")

    with image_col:
        pass  # image displayed later

    car_labels = [f"{c['brand']} {c['model']} ({c['body_type']})" for c in cars]
    selected_label = st.selectbox("Select Car", car_labels)

    selected_car = next(
        c for c in cars
        if f"{c['brand']} {c['model']} ({c['body_type']})" == selected_label
    )

    # IMAGE TOP RIGHT
    with image_col:
        img_path = selected_car.get("image")
        if img_path and os.path.exists(img_path):
            st.image(img_path, width=160)

    # CAR INFO — ORIGINAL 3 COLUMN LAYOUT
    st.markdown("### 🚗 Car Details")

    colA, colB, colC = st.columns(3)

    with colA:
        st.write(f"**Brand:** {selected_car['brand']}")
        st.write(f"**Model:** {selected_car['model']}")
        st.write(f"**Body Type:** {selected_car['body_type']}")

    with colB:
        st.write(f"**Fuel Type:** {selected_car['fuel_type']}")
        st.write(f"**Transmission:** {selected_car['transmission']}")
        st.write(f"**Mileage:** {selected_car['mileage']}")

    with colC:
        st.write(f"**Engine:** {selected_car['engine_capacity']}")
        st.write(f"**Seating:** {selected_car['seating_capacity']}")
        st.write(f"**Price / Day:** ₹{selected_car['price']}")

    # DATES
    st.markdown("### 📅 Rental Dates")
    d1, d2 = st.columns(2)

    with d1:
        pickup_date = st.date_input("Pickup Date", date.today())

    with d2:
        return_date = st.date_input("Return Date", date.today() + timedelta(days=1))

    total_days = max((return_date - pickup_date).days, 1)
    total_cost = total_days * selected_car["price"]

    st.markdown(f"## Total Cost: ₹{total_cost}")

    # CONFIRM
    if st.button("Confirm Booking"):
        try:
            r = requests.post(
                f"{BACKEND_URL}/api/book",
                json={
                    "user_id": st.session_state["user"]["_id"],
                    "car_id": selected_car["_id"],
                }
            )
            if r.json().get("success"):
                st.success("✅ Booking recorded successfully")
        except Exception as e:
            st.error(f"Error: {e}")


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

