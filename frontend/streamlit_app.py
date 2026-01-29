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
# LOGIN + SIGNUP PAGE
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
                st.session_state["page"] = "home"
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
            data = safe_post(
                f"{BACKEND_URL}/api/signup",
                {"name": name, "email": email, "phone": phone, "password": password}
            )
            if data and data.get("success"):
                st.success("Account created! Please login.")
            else:
                st.error("Signup failed")


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
# RECOMMENDATION TILE PAGE
# ------------------------------------------------------------
def recommendations_page():
    st.title("🔍 Choose Your Car Preferences")

    # Tile images
    tile_images = {
        "Brand": "assets/brand.jpg",
        "Fuel_Type": "assets/fuel.jpg",
        "Body_Type": "assets/body.jpg",
        "Transmission": "assets/transmission.jpg",
    }

    options = {
        "Brand": ["Toyota", "Honda", "Hyundai", "BMW"],
        "Fuel_Type": ["Petrol", "Diesel", "Electric"],
        "Body_Type": ["SUV", "Sedan", "Hatchback"],
        "Transmission": ["Manual", "Automatic"]
    }

    tile_css = """
        <style>
        .tile-img {
            width: 100%;
            height: 150px;
            border-radius: 16px;
            object-fit: cover;
            cursor: pointer;
            transition: 0.2s;
        }
        .tile-img:hover {
            transform: scale(1.03);
            opacity: 0.92;
        }
        </style>
    """
    st.markdown(tile_css, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    for idx, key in enumerate(tile_images.keys()):
        col = [col1, col2, col3, col4][idx]

        with col:
            img_b64 = base64.b64encode(open(tile_images[key], "rb").read()).decode()
            if st.button(f" ", key=f"tile_{key}"):
                st.session_state[f"open_{key}"] = not st.session_state.get(f"open_{key}", False)

            st.markdown(
                f"<img src='data:image/jpeg;base64,{img_b64}' class='tile-img'>",
                unsafe_allow_html=True,
            )

            if st.session_state.get(f"open_{key}", False):
                choice = st.selectbox(
                    f"Select {key}", options[key], key=f"sel_{key}"
                )
                st.session_state["filters"][key] = choice

    # Recommend button
    st.write("---")
    if st.button("📌 Recommend Cars"):
        payload = st.session_state["filters"].copy()
        payload["min_mileage"] = 10
        payload["max_engine_cc"] = 3500

        rec = safe_post(f"{BACKEND_URL}/recommend", payload)
        if rec:
            st.session_state["recommended_cars"] = rec
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

    # Show recommended FIRST
    if st.session_state["recommended_cars"]:
        st.write("### ⭐ Recommended For You")

        for car in st.session_state["recommended_cars"]:
            cols = st.columns([4, 1])
            cols[0].write(f"**{car['Brand']} {car['Model']}** — {car['Engine_CC']}cc")
            if cols[1].button("Select", key=f"r_{car['Car_ID']}"):
                st.session_state["selected_car"] = car

    st.write("---")

    # Dropdown list of all cars
    st.write("### 🚗 All Cars")

    labels = [f"{c['brand']} {c['model']}" for c in cars]

    # Preselect recommended
    default_index = 0
    if st.session_state["selected_car"]:
        recommended_label = (
            f"{st.session_state['selected_car']['Brand']} {st.session_state['selected_car']['Model']}"
        )
        if recommended_label in labels:
            default_index = labels.index(recommended_label)

    selected_label = st.selectbox("Select Car", labels, index=default_index)

    selected_car = next(c for c in cars if f"{c['brand']} {c['model']}" == selected_label)
    price = selected_car["price"]

    # Dates
    col1, col2 = st.columns(2)
    with col1:
        pickup = st.date_input("Pickup Date", date.today())
    with col2:
        drop = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((drop - pickup).days, 1)
    st.write(f"### 💰 Total Cost: ₹{days * price}")

    if st.button("Confirm Booking"):
        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {"user_id": st.session_state["user"]["_id"], "car_id": selected_car["_id"]},
        )
        if r and r.get("success"):
            st.success("Booking confirmed!")


# ------------------------------------------------------------
# ROUTER
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
