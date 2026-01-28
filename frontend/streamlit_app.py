import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
BACKEND_URL = os.environ.get("BACKEND_URL")
if not BACKEND_URL:
    st.error("BACKEND_URL environment variable is missing!")
    st.stop()

st.set_page_config(page_title="Car Rental System", layout="wide")

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"


# ------------------------------------------------------------
# BACKGROUND IMAGE
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
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass  # Ignore if missing


# ------------------------------------------------------------
# LOGIN SCREEN
# ------------------------------------------------------------
def login_screen():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            r = requests.post(f"{BACKEND_URL}/api/login",
                              json={"email": email, "password": password})
            if r.status_code == 200:
                st.session_state["user"] = r.json()["user"]
                st.session_state["page"] = "home"
                st.rerun()
            else:
                st.error("Invalid credentials")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

    st.write("Don't have an account?")
    if st.button("Go to Sign Up"):
        st.session_state["page"] = "signup"
        st.rerun()


# ------------------------------------------------------------
# SIGNUP SCREEN
# ------------------------------------------------------------
def signup_screen():
    st.title("📝 Sign Up")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        try:
            r = requests.post(f"{BACKEND_URL}/api/signup",
                              json={"name": name, "email": email, "phone": phone, "password": password})
            data = r.json()

            if data.get("success"):
                st.success("Account created successfully! Please Login.")
            else:
                st.error("User already exists")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

    if st.button("Back to Login"):
        st.session_state["page"] = "login"
        st.rerun()


# ------------------------------------------------------------
# HOME SCREEN
# ------------------------------------------------------------
def home_screen():
    user = st.session_state["user"]
    set_background("assets/123.jpg")

    st.title("🚗 AI Powered Car Rental System")
    st.write(f"Welcome, **{user['name']}**")

    if st.button("Book a Car"):
        st.session_state["page"] = "book"
        st.rerun()


# ------------------------------------------------------------
# BOOKING SCREEN
# ------------------------------------------------------------
def book_screen():
    st.title("📅 Book a Car")

    try:
        r = requests.get(f"{BACKEND_URL}/api/cars")
        cars = r.json()
    except:
        st.error("Error fetching cars from backend.")
        return

    car_names = [
        f"{c['brand']} {c['model']} ({c['body_type']})"
        for c in cars
    ]

    selected_label = st.selectbox("Select Car", car_names)

    car = next(c for c in cars if
               f"{c['brand']} {c['model']} ({c['body_type']})" == selected_label)

    # car image
    if os.path.exists(car["image"]):
        st.image(car["image"], width=250)

    st.subheader("Car Details")
    st.write(f"**Brand:** {car['brand']}")
    st.write(f"**Model:** {car['model']}")
    st.write(f"**Price:** ₹{car['price']} / day")

    # Dates
    start_date = st.date_input("Pickup Date", date.today())
    end_date = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((end_date - start_date).days, 1)
    st.write(f"### Total Cost: ₹{days * car['price']}")

    if st.button("Confirm Booking"):
        try:
            r = requests.post(f"{BACKEND_URL}/api/book",
                              json={"user_id": st.session_state["user"]["_id"],
                                    "car_id": car["_id"]})
            if r.json().get("success"):
                st.success("Booking Confirmed!")
        except Exception as e:
            st.error(f"Error: {e}")


# ------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------
if st.session_state["user"] is None:
    if st.session_state["page"] == "signup":
        signup_screen()
    else:
        login_screen()
else:
    if st.session_state["page"] == "book":
        book_screen()
    else:
        home_screen()
