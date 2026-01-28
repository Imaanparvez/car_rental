import streamlit as st
import requests
import os
from datetime import date, datetime
import base64

# ------------------------------
# CONFIG
# ------------------------------
BACKEND_URL = os.environ.get("BACKEND_URL")

if not BACKEND_URL:
    st.error("BACKEND_URL not found in environment variables.")
    st.stop()

st.set_page_config(page_title="Car Rental System", layout="wide")

if "user" not in st.session_state:
    st.session_state["user"] = None


# ---------------------------------------------------
# BACKGROUND IMAGE
# ---------------------------------------------------
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
        pass  # Ignore if missing


# ---------------------------------------------------
# NAV BAR
# ---------------------------------------------------
def nav_bar():
    st.markdown(
        """
        <style>
        .nav-btn { margin-right: 20px; font-size:18px; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    cols = st.columns([4,1,1])

    with cols[1]:
        if st.button("Home"):
            st.session_state["page"] = "home"

    if st.session_state["user"]:
        with cols[2]:
            if st.button("Logout"):
                st.session_state["user"] = None
                st.session_state["page"] = "login"


# ---------------------------------------------------
# LOGIN SCREEN
# ---------------------------------------------------
def login_screen():
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        r = requests.post(
            f"{BACKEND_URL}/api/login",
            json={"email": email, "password": password}
        )

        try:
            data = r.json()
        except:
            st.error("Backend not responding. Check BACKEND_URL.")
            return

        if "user" in data:
            st.session_state["user"] = data["user"]
            st.session_state["page"] = "home"
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials")


# ---------------------------------------------------
# SIGNUP SCREEN
# ---------------------------------------------------
def signup_screen():
    st.title("Create Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        r = requests.post(
            f"{BACKEND_URL}/api/signup",
            json={"name": name, "email": email, "phone": phone, "password": password}
        )

        try:
            data = r.json()
        except:
            st.error("Backend error")
            return

        if data.get("success"):
            st.success("Account created! Go to Login.")
        else:
            st.error("User already exists")


# ---------------------------------------------------
# CAR LISTING + BOOKING
# ---------------------------------------------------
def home_screen():
    set_background("assets/123.jpg")

    st.title("Available Cars")

    # Fetch cars
    r = requests.get(f"{BACKEND_URL}/api/cars")

    try:
        cars = r.json()
    except:
        st.error("Error loading cars from backend.")
        return

    # Car DISPLAY CARDS
    cols = st.columns(3)

    for i, car in enumerate(cars):
        with cols[i % 3]:
            # FIX IMAGE PATH
            img_path = "assets/" + car["image"].split("assets/")[-1]

            st.image(img_path, use_column_width=True)

            st.subheader(f"{car['brand']} {car['model']}")
            st.write(f"**Type:** {car['body_type']}")
            st.write(f"**Fuel:** {car['fuel_type']}")
            st.write(f"**Transmission:** {car['transmission']}")
            st.write(f"**Mileage:** {car['mileage']}")
            st.write(f"**Engine:** {car['engine_capacity']}")
            st.write(f"**Seats:** {car['seating_capacity']}")

            # DATE PICKERS
            pickup = st.date_input(
                "Pickup Date",
                min_value=date.today(),
                key=f"pickup_{i}"
            )
            dropoff = st.date_input(
                "Dropoff Date",
                min_value=date.today(),
                key=f"dropoff_{i}"
            )

            # Calculate Price
            if dropoff >= pickup:
                days = (dropoff - pickup).days + 1
                total_price = car["price"] * days
                st.write(f"### Total Price: ₹{total_price}")
            else:
                st.warning("Dropoff date must be after pickup date.")
                continue

            if st.button(f"Book {car['model']}", key=f"book_{i}"):
                user = st.session_state["user"]
                if not user:
                    st.error("Login first!")
                    return

                r = requests.post(
                    f"{BACKEND_URL}/api/book",
                    json={"user_id": user["_id"], "car_id": car["_id"]}
                )

                if r.json().get("success"):
                    st.success("Booking Confirmed!")
                else:
                    st.error("Booking failed!")


# ---------------------------------------------------
# PAGE HANDLING
# ---------------------------------------------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

nav_bar()

if st.session_state["page"] == "login":
    login_screen()
elif st.session_state["page"] == "signup":
    signup_screen()
else:
    home_screen()
