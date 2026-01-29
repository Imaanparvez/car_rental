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

if "filters" not in st.session_state:
    st.session_state["filters"] = {}

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
    except Exception:
        pass


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
            st.code(r.text)
    except Exception as e:
        st.error("❌ Backend connection failed")
        st.write(str(e))
    return None


def safe_get(url):
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"❌ API Error {r.status_code}")
            st.code(r.text)
    except Exception as e:
        st.error("❌ Backend connection failed")
        st.write(str(e))
    return None


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
            data = safe_post(
                f"{BACKEND_URL}/api/signup",
                {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "password": password
                }
            )
            if data and data.get("success"):
                st.success("Account created! Please login.")
            else:
                st.error("Signup failed")


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
def render_sidebar():
    st.sidebar.success(f"Welcome, {st.session_state['user']['name']} 👋")

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
# RECOMMENDATION TILE PAGE
# ------------------------------------------------------------
def recommendations_page():
    st.title("🔍 AI Car Recommendations")
    st.markdown("### Choose a category")

    tile_css = """
    <style>
    .tile-box {
        background-size: cover !important;
        background-position: center !important;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 20px;
        color: white;
        font-size: 28px;
        font-weight: bold;
        text-shadow: 2px 2px 6px black;
    }
    </style>
    """
    st.markdown(tile_css, unsafe_allow_html=True)

    # Helper: load image
    def load_b64(path):
        try:
            return base64.b64encode(open(path, "rb").read()).decode()
        except:
            return ""

    # Expandable tile
    def tile(label, bg_path, options, keyname):
        bg = load_b64(bg_path)

        with st.expander(f" ", expanded=False):
            st.markdown(
                f"""
                <div class="tile-box" style="background-image:url('data:image/jpeg;base64,{bg}')">
                    {label}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write(f"**Select {label}:**")
            for opt in options:
                if st.button(opt, key=f"{keyname}_{opt}"):
                    st.session_state["filters"] = {keyname: opt}
                    st.session_state["page"] = "book"
                    st.rerun()

    # 2×2 Layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        tile("Brand", "assets/brand.jpg",
             ["Toyota", "Honda", "Hyundai", "BMW"],
             "Brand")

    with col2:
        tile("Fuel Type", "assets/fuel.jpg",
             ["Petrol", "Diesel", "Electric"],
             "Fuel_Type")

    with col3:
        tile("Body Type", "assets/body.jpg",
             ["SUV", "Sedan", "Hatchback"],
             "Body_Type")

    with col4:
        tile("Transmission", "assets/transmission.jpg",
             ["Manual", "Automatic"],
             "Transmission")


# ------------------------------------------------------------
# BOOKING PAGE
# ------------------------------------------------------------
def book_page():
    st.markdown("## 📅 Book a Car")

    filters = st.session_state.get("filters", {})

    # -------------------------------
    # AI RECOMMENDATION (FILTER PRE-APPLIED)
    # -------------------------------
    st.markdown("### 🎯 For You (AI Recommended Cars)")
    payload = {
        "Brand": filters.get("Brand", ""),
        "Fuel_Type": filters.get("Fuel_Type", ""),
        "Transmission": filters.get("Transmission", ""),
        "Body_Type": filters.get("Body_Type", ""),
        "min_mileage": 10,
        "max_engine_cc": 3500
    }

    data = safe_post(f"{BACKEND_URL}/recommend", payload)

    if data:
        for car in data:
            st.write(f"**{car['Brand']} {car['Model']}**")
            st.write(f"Mileage: {car['Mileage']} | Engine: {car['Engine_CC']} CC")
            if st.button(f"Select {car['Model']}", key=f"select_{car['Car_ID']}"):
                st.session_state["selected_car"] = car
                st.success("Car selected!")

    # -------------------------------
    # Fetch All Cars
    # -------------------------------
    st.markdown("---")
    st.markdown("### 📋 All Cars")

    cars = safe_get(f"{BACKEND_URL}/api/cars")
    if not cars:
        return

    car_labels = [f"{c['brand']} {c['model']} ({c['body_type']})" for c in cars]
    selected_label = st.selectbox("Select Car", car_labels)

    selected_car = next(
        c for c in cars
        if f"{c['brand']} {c['model']} ({c['body_type']})" == selected_label
    )

    price = selected_car["price"]

    # -------------------------------
    # Dates + Total Cost
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
        result = safe_post(
            f"{BACKEND_URL}/api/book",
            {
                "user_id": st.session_state["user"]["_id"],
                "car_id": selected_car.get("_id", selected_car.get("Car_ID"))
            }
        )
        if result and result.get("success"):
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
    elif st.session_state["page"] == "recommendations":
        recommendations_page()
    elif st.session_state["page"] == "book":
        book_page()
