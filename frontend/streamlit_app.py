st.write("DEBUG BACKEND_URL =", os.environ.get("BACKEND_URL"))
import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64

API_URL = os.environ.get("BACKEND_URL")

st.set_page_config(page_title="AI Powered Car Rental System", layout="wide")

if "user" not in st.session_state:
    st.session_state["user"] = None

def set_background(image_path):
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

# ------------------------------
# LOGIN PAGE
# ------------------------------
def login_screen():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        r = requests.post(f"{API_URL}/api/login", json={
            "email": email,
            "password": password
        })

        if r.status_code == 200:
            st.session_state["user"] = r.json()["user"]
            st.success("Login successful!")
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error("Invalid credentials")


# ------------------------------
# SIGN UP
# ------------------------------
def signup_screen():
    st.title("📝 Sign Up")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        r = requests.post(f"{API_URL}/api/signup", json={
            "name": name,
            "email": email,
            "phone": phone,
            "password": password
        })

        if r.json().get("success"):
            st.success("Account created! Please login.")
        else:
            st.error("User already exists")


# ------------------------------
# HOME PAGE
# ------------------------------
def home_screen():
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
        unsafe_allow_html=True,
    )


# ------------------------------
# BOOK CAR PAGE
# ------------------------------
def book_screen():
    st.title("📅 Book a Car")

    cars = requests.get(f"{API_URL}/api/cars").json()

    car_names = [f"{c['brand']} {c['model']} ({c['body_type']})" for c in cars]
    car_map = {cname: car for cname, car in zip(car_names, cars)}

    selected = st.selectbox("Select Car", car_names)
    selected_car = car_map[selected]

    st.write("### Car Details")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Brand:** {selected_car['brand']}")
        st.write(f"**Model:** {selected_car['model']}")
        st.write(f"**Body Type:** {selected_car['body_type']}")
    with col2:
        st.write(f"**Fuel:** {selected_car['fuel_type']}")
        st.write(f"**Transmission:** {selected_car['transmission']}")

    if st.button("Confirm Booking"):
        r = requests.post(f"{API_URL}/api/book", json={
            "user_id": st.session_state["user"]["_id"],
            "car_id": selected_car["_id"]
        })

        if r.json().get("success"):
            st.success("✅ Booking confirmed!")
        else:
            st.error("Booking failed")


# -----------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------
if st.session_state["user"] is None:
    page = st.sidebar.radio("Menu", ["Login", "Sign Up"])
    if page == "Login":
        login_screen()
    else:
        signup_screen()

else:
    st.sidebar.success(f"Logged in as {st.session_state['user']['name']}")

    page = st.sidebar.radio(
        "Navigation", ["Home", "Book a Car", "Logout"]
    )

    if page == "Home":
        home_screen()
    elif page == "Book a Car":
        book_screen()
    elif page == "Logout":
        st.session_state["user"] = None
        st.rerun()




